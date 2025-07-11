# -----------------------------------------------------------
# Secrets para las credenciales de la DB de Auth y JWT Secret
# -----------------------------------------------------------
resource "kubernetes_secret_v1" "auth_db_credentials" {
  metadata {
    name      = "auth-db-credentials"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  data = {
    # Las credenciales y la URL de conexión ahora se construyen a partir de variables
    # Terraform codificará automáticamente los valores en Base64.
    "POSTGRES_USER"     = var.auth_db_user
    "POSTGRES_PASSWORD" = var.auth_db_password
    "POSTGRES_DB"       = var.auth_db_name
    
    # La DATABASE_URL para la aplicación de auth.
    # Esta debe coincidir con las credenciales de POSTGRES_USER y POSTGRES_PASSWORD.
    # El hostname 'auth-db-service' se refiere al servicio de Kubernetes para la DB.
    "DATABASE_URL"      = "postgresql://${var.auth_db_user}:${var.auth_db_password}@auth-db-service:5432/${var.auth_db_name}"
    
    # Secreto JWT para la aplicación de Auth. ¡IMPORTANTE! Cambia esto por un secreto real y seguro en producción
    "JWT_SECRET"        = var.jwt_secret
  }
  type = "Opaque"
}

# -----------------------------------------------------------
# ConfigMap para el script de inicialización de la DB de Auth
# -----------------------------------------------------------
resource "kubernetes_config_map_v1" "auth_db_init_script" {
  metadata {
    name      = "auth-db-init-script"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  data = {
    # Asegúrate que el archivo 'initAuth.sql' exista en el mismo directorio que este .tf
    "init-auth-db.sql" = file("${path.module}/initAuth.sql")
  }
}

# -----------------------------------------------------------
# Despliegue de la Base de Datos PostgreSQL para el servicio de Auth
# -----------------------------------------------------------

resource "kubernetes_persistent_volume_claim_v1" "auth_postgres_pvc" {
  metadata {
    name      = "auth-postgres-data-pvc"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
    storage_class_name = "standard"
  }
}

resource "kubernetes_deployment_v1" "auth_postgres_deployment" {
  metadata {
    name      = "auth-postgres-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "auth-postgres"
    }
  }

  spec {
    replicas = 1
    strategy { # Usar estrategia Recreate para DBs con PVCs para asegurar una correcta inicialización
      type = "Recreate"
    }
    selector {
      match_labels = {
        app = "auth-postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "auth-postgres"
        }
      }
      spec {
        container {
          name  = "auth-postgres"
          image = "postgres:15" # Imagen oficial de PostgreSQL
          port {
            container_port = 5432 # Puerto estándar de PostgreSQL
          }
          env_from { # Inyecta las credenciales POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB desde el Secret
            secret_ref {
              name = kubernetes_secret_v1.auth_db_credentials.metadata[0].name
            }
          }
          env { # PGDATA se define directamente para el directorio de datos de PostgreSQL
            name  = "PGDATA"
            value = "/var/lib/postgresql/data/pgdata"
          }
          volume_mount { # Monta el PVC para persistir los datos de la DB
            name       = "auth-postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }
          # --- AÑADIR ESTE BLOQUE: Montar el ConfigMap con el script de inicialización ---
          volume_mount {
            name       = "auth-db-init-script-volume"
            mount_path = "/docker-entrypoint-initdb.d/" # Ruta donde la imagen de Postgres busca scripts de inicialización
            read_only  = true
          }
          # --- FIN DEL BLOQUE ---
          # --- OPCIONAL: Añadir readinessProbe para la DB de auth (muy recomendado) ---
          readiness_probe {
            exec {
              # Usar el usuario de la DB para la comprobación de salud
              command = ["pg_isready", "-U", var.auth_db_user, "-h", "localhost", "-p", "5432"]
            }
            initial_delay_seconds = 30 # Aumentar el retraso inicial
            period_seconds        = 10 # Comprobar con menos frecuencia
            timeout_seconds       = 5  # Dar más tiempo al comando
            failure_threshold     = 3  # Reducir fallos antes de marcar como no listo
          }
          # --- FIN OPCIONAL ---
          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }
        }
        volume {
          name = "auth-postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.auth_postgres_pvc.metadata[0].name
          }
        }
        # --- AÑADIR ESTE BLOQUE: Definir el volumen para el ConfigMap ---
        volume {
          name = "auth-db-init-script-volume"
          config_map {
            name = kubernetes_config_map_v1.auth_db_init_script.metadata[0].name
          }
        }
        # --- FIN DEL BLOQUE ---
      }
    }
  }
  depends_on = [
    kubernetes_persistent_volume_claim_v1.auth_postgres_pvc,
    kubernetes_secret_v1.auth_db_credentials,
    kubernetes_config_map_v1.auth_db_init_script # Dependencia del ConfigMap
  ]
}

resource "kubernetes_service_v1" "auth_postgres_service" {
  metadata {
    name      = "auth-db-service" # Nombre de host interno que la app de auth usará para la DB
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "auth-postgres"
    }
  }
  spec {
    selector = {
      app = "auth-postgres"
    }
    port {
      port        = 5432
      target_port = 5432
    }
    type = "ClusterIP" # Servicio accesible solo dentro del clúster
  }
  depends_on = [kubernetes_deployment_v1.auth_postgres_deployment]
}

# -----------------------------------------------------------
# Despliegue del Microservicio de Autenticación (Python)
# -----------------------------------------------------------

resource "kubernetes_deployment_v1" "auth_deployment" {
  metadata {
    name      = "auth-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "auth"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "auth"
      }
    }
    template {
      metadata {
        labels = {
          app = "auth"
        }
      }
      spec {
        container {
          name  = "auth-service"
          # !!! IMPORTANTE: ACTUALIZA ESTE SHA256 CON EL DIGEST DE TU IMAGEN PYTHON RECIÉN CONSTRUIDA Y PUSHEADA !!!
          image = "us-east1-docker.pkg.dev/lab-reservations-465014/reservas-repo/auth@sha256:ed53f5edb15ea758378403574f40c72d300664187dd5e519323c77e56a79137f"          
          port {
            container_port = 8000 # Puerto que tu app Python expone (ej. para Gunicorn/Uvicorn)
          }
          env {
            name  = "PORT"
            value = "8000" # Variable de entorno PORT para la app Python
          }
          
          # --- Inyección de variables de entorno desde el Secret ---
          # Kubernetes decodificará los valores Base64 automáticamente antes de inyectarlos.
          env {
            name  = "DATABASE_URL" # Nombre de la variable de entorno que tu app Python espera
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.auth_db_credentials.metadata[0].name # Nombre del Secret
                key  = "DATABASE_URL" # Clave específica dentro del Secret
              }
            }
          }
          env {
            name  = "JWT_SECRET" # Nombre de la variable de entorno para el secreto JWT
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.auth_db_credentials.metadata[0].name
                key  = "JWT_SECRET"
              }
            }
          }
          # -------------------------------------------------------------------------

          env { # Variable de entorno SSL para la conexión a la DB
            name  = "SSL"
            value = "false"
          }
          # Se asume que el Dockerfile de tu aplicación Python define el CMD o ENTRYPOINT
          # correcto para iniciar la aplicación (ej. CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]).
          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
  depends_on = [
    kubernetes_service_v1.auth_postgres_service,
    kubernetes_secret_v1.auth_db_credentials
  ]
}

resource "kubernetes_service_v1" "auth_service" {
  metadata {
    name      = "auth-service" # Nombre del servicio interno para la app Python
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "auth"
    }
  }
  spec {
    selector = {
      app = "auth"
    }
    port {
      port        = 80 # Puerto del Service (interno al clúster)
      target_port = 8000 # Puerto del contenedor al que se dirige el tráfico (puerto de la app Python)
    }
    type = "ClusterIP" # Servicio accesible solo dentro del clúster
  }
  depends_on = [kubernetes_deployment_v1.auth_deployment]
}
