# k8s-deployments/laboratorios_service.tf

# -----------------------------------------------------------
# Secrets para las credenciales de la DB de Laboratorios
# -----------------------------------------------------------
resource "kubernetes_secret_v1" "laboratorios_db_credentials" {
  metadata {
    name      = "laboratorios-db-credentials"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  # Los valores se codificarán automáticamente en base64 por Terraform al guardarse en Kubernetes.
  # Este Secret es usado EXCLUSIVAMENTE por el Deployment de la DB de PostgreSQL para su inicialización.
  # y por el microservicio de laboratorios para conectarse a la DB.
  data = {
    "POSTGRES_USER"     = var.laboratorios_db_user
    "POSTGRES_PASSWORD" = var.laboratorios_db_password
    "POSTGRES_DB"       = var.laboratorios_db_name
    "DATABASE_URL"      = "postgresql://${var.laboratorios_db_user}:${var.laboratorios_db_password}@laboratorios-db-service:5432/${var.laboratorios_db_name}"
  }
  type = "Opaque" # Tipo de secreto estándar
}

# -----------------------------------------------------------
# ConfigMap para el script de inicialización de la DB
# -----------------------------------------------------------
resource "kubernetes_config_map_v1" "laboratorios_db_init_script" {
  metadata {
    name      = "laboratorios-db-init-script"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  data = {
    "init-laboratorios-db.sql" = file("${path.module}/init-laboratorios-db.sql") # Asegúrate que la ruta sea correcta
  }
}

# -----------------------------------------------------------
# Despliegue de la Base de Datos PostgreSQL para el servicio de Laboratorios
# -----------------------------------------------------------

resource "kubernetes_persistent_volume_claim_v1" "laboratorios_postgres_pvc" {
  metadata {
    name      = "laboratorios-postgres-data-pvc"
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

resource "kubernetes_deployment_v1" "laboratorios_postgres_deployment" {
  metadata {
    name      = "laboratorios-postgres-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "laboratorios-postgres"
    }
  }

  spec {
    replicas = 1
    strategy { # Usar estrategia Recreate para DBs con PVCs para asegurar una correcta inicialización
      type = "Recreate"
    }
    selector {
      match_labels = {
        app = "laboratorios-postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "laboratorios-postgres"
        }
      }
      spec {
        container {
          name  = "laboratorios-postgres"
          image = "postgres:15" # Imagen oficial de PostgreSQL
          port {
            container_port = 5432 # Puerto estándar de PostgreSQL
          }
          # Usar env_from para inyectar las variables de inicialización de PostgreSQL desde el Secret.
          # Aunque el script lo hará, esto asegura que las variables estén presentes.
          env_from {
            secret_ref {
              name = kubernetes_secret_v1.laboratorios_db_credentials.metadata[0].name
            }
          }
          env { # PGDATA se define directamente para el directorio de datos de PostgreSQL
            name  = "PGDATA"
            value = "/var/lib/postgresql/data/pgdata"
          }
          volume_mount { # Monta el PVC para persistir los datos de la DB
            name       = "laboratorios-postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }
          # Montar el ConfigMap con el script de inicialización
          volume_mount {
            name       = "laboratorios-db-init-script-volume"
            mount_path = "/docker-entrypoint-initdb.d/" # Ruta donde la imagen de Postgres busca scripts de inicialización
            read_only  = true
          }
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
          name = "laboratorios-postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.laboratorios_postgres_pvc.metadata[0].name
          }
        }
        # Definir el volumen para el ConfigMap
        volume {
          name = "laboratorios-db-init-script-volume"
          config_map {
            name = kubernetes_config_map_v1.laboratorios_db_init_script.metadata[0].name
          }
        }
      }
    }
  }
  depends_on = [
    kubernetes_persistent_volume_claim_v1.laboratorios_postgres_pvc,
    kubernetes_secret_v1.laboratorios_db_credentials,
    kubernetes_config_map_v1.laboratorios_db_init_script # Dependencia del ConfigMap
  ]
}

resource "kubernetes_service_v1" "laboratorios_postgres_service" {
  metadata {
    name      = "laboratorios-db-service" # Nombre de host interno que la app de laboratorios usará para la DB
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "laboratorios-postgres"
    }
  }
  spec {
    selector = {
      app = "laboratorios-postgres"
    }
    port {
      port        = 5432
      target_port = 5432
    }
    type = "ClusterIP" # Servicio accesible solo dentro del clúster
  }
  depends_on = [kubernetes_deployment_v1.laboratorios_postgres_deployment]
}

# -----------------------------------------------------------
# Despliegue del Microservicio de Gestión de Laboratorios (Python)
# -----------------------------------------------------------

resource "kubernetes_deployment_v1" "laboratorios_deployment" {
  metadata {
    name      = "laboratorios-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "laboratorios"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "laboratorios"
      }
    }
    template {
      metadata {
        labels = {
          app = "laboratorios"
        }
      }
      spec {
        container {
          name  = "laboratorios-service"
          # !!! IMPORTANTE: ACTUALIZA ESTE SHA256 CON EL DIGEST DE TU IMAGEN PYTHON RECIÉN CONSTRUIDA Y PUSHEADA !!!
          # Este SHA debe ser el de la imagen de tu aplicación 'laboratorios' (Python).
          image = "us-east1-docker.pkg.dev/lab-reservations-465014/reservas-repo/laboratorios@sha256:f8d7299a7fcf7964ad704b596cb09d6f30e7f78772a0f86db8418d8ba0fd21a7"
          port {
            container_port = 8000 # Puerto que tu app Python expone (según Dockerfile)
          }
          env {
            name  = "PORT"
            value = "8000" # Variable de entorno PORT para la app Python
          }
          
          # Inyección de DATABASE_URL desde el secret para evitar hardcodear credenciales.
          env {
            name  = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.laboratorios_db_credentials.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }

          env { # Variable de entorno SSL para la conexión a la DB
            name  = "SSL"
            value = "false"
          }
          # Se elimina la línea 'command'. El CMD de tu Dockerfile de Python es suficiente.
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
    kubernetes_service_v1.laboratorios_postgres_service,
    kubernetes_secret_v1.laboratorios_db_credentials
  ]
}

resource "kubernetes_service_v1" "laboratorios_service" {
  metadata {
    name      = "laboratorios-service" # Nombre del servicio interno para la app Python
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "laboratorios"
    }
  }
  spec {
    selector = {
      app = "laboratorios"
    }
    port {
      port        = 80 # Puerto del Service (interno al cluster)
      target_port = 8000 # Puerto del contenedor que expone la app Python
    }
    type = "ClusterIP" # Servicio accesible solo dentro del clúster
  }
  depends_on = [kubernetes_deployment_v1.laboratorios_deployment]
}
