# -----------------------------------------------------------
# Despliegue de la Base de Datos PostgreSQL
# -----------------------------------------------------------

# Define un Namespace específico para la aplicación reservas-horarios y PostgreSQL.
# Se define aquí para que esté disponible para ambos la base de datos y la app
resource "kubernetes_namespace" "reservas_horarios_namespace" {
  metadata {
    name = "reservas-horarios-app"
  }
}

# Paso 1: Definir un PersistentVolumeClaim (PVC) para los datos de la DB
# Esto solicita almacenamiento persistente a Google Cloud (un Persistent Disk).
resource "kubernetes_persistent_volume_claim_v1" "postgres_pvc" {
  metadata {
    name      = "postgres-data-pvc"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name # Mismo namespace que la app
  }
  spec {
    access_modes = ["ReadWriteOnce"] # Solo un Pod puede escribir a la vez
    resources {
      requests = {
        storage = "10Gi" # Solicita 10 GB de almacenamiento (ajusta según necesites)
      }
    }
    storage_class_name = "standard" # GKE suele tener un StorageClass por defecto, puedes omitirlo o especificarlo
  }
  depends_on = [kubernetes_namespace.reservas_horarios_namespace]
}

# Paso 2: Desplegar el contenedor de PostgreSQL (kubernetes_deployment_v1)
resource "kubernetes_deployment_v1" "postgres_deployment" {
  metadata {
    name      = "postgres-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "postgres"
    }
  }

  spec {
    replicas = 1 # Una sola instancia de la DB por ahora
    # Cambia la estrategia de actualización para evitar el deadlock con el PVC.
    # 'Recreate' termina el pod antiguo antes de crear el nuevo.
    strategy {
      type = "Recreate"
    }
    selector {
      match_labels = {
        app = "postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }
      spec {
        container {
          name  = "postgres"
          image = "postgres:15-alpine" # Imagen de PostgreSQL, como en tu docker-compose
          port {
            container_port = 5432 # Puerto estándar de PostgreSQL
          }
          # Carga las variables de entorno directamente desde el Secret de Kubernetes.
          # Esto inyectará POSTGRES_USER, POSTGRES_PASSWORD y POSTGRES_DB.
          env_from {
            secret_ref {
              name = kubernetes_secret_v1.db_credentials.metadata[0].name
            }
          }
          env {
            name  = "PGDATA"
            value = "/var/lib/postgresql/data/pgdata" # This is the new data subdirectory
          }
          volume_mount {
            name       = "postgres-data"
            mount_path = "/var/lib/postgresql/data" # Ruta donde PostgreSQL guarda sus datos
          }
        }
        volume {
          name = "postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.postgres_pvc.metadata[0].name
          }
        }
      }
    }
  }
  depends_on = [kubernetes_persistent_volume_claim_v1.postgres_pvc]
}

# Paso 3: Crear un Servicio interno para PostgreSQL (kubernetes_service_v1)
# Este servicio permitirá que tu aplicación se conecte a la DB usando el nombre 'db-service'
resource "kubernetes_service_v1" "postgres_service" {
  metadata {
    name      = "db-service" # ¡Este será el nombre de host que tu app usará para la DB!
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "postgres"
    }
  }
  spec {
    selector = {
      app = "postgres"
    }
    port {
      port        = 5432 # Puerto en el que el Service escucha
      target_port = 5432 # Puerto del contenedor al que se redirige el tráfico
    }
    type = "ClusterIP" # Accesible solo dentro del clúster
  }
  depends_on = [kubernetes_deployment_v1.postgres_deployment]
}
# -----------------------------------------------------------
# Despliegue del Microservicio de Reservas-Horarios
# -----------------------------------------------------------


resource "kubernetes_deployment_v1" "reservas_horarios_deployment" {
  metadata {
    name      = "reservas-horarios-deployment"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "reservas-horarios"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "reservas-horarios"
      }
    }
    template {
      metadata {
        labels = {
          app = "reservas-horarios"
        }
      }
      spec {
        container {
          name  = "reservas-horarios-service"
          # IMPORTANT: Verify this image path and SHA256 matches your pushed image
          image = "us-east1-docker.pkg.dev/lab-reservations-465014/reservas-repo/reservas-horarios@sha256:17d24a5d4f14bf94cade635a0ca389b55292ee0cdfb13e7ba22482d055ba6794"
          port {
            container_port = 8000
          }
          env {
            # Inyecta la variable de entorno DATABASE_URL desde nuestro Secret.
            name  = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.db_credentials.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }

           resources {
            requests = { # Lo mínimo que el Pod necesita para ser programado
              cpu    = "100m" # 0.1 de un núcleo de CPU
              memory = "128Mi" # 128 Megabytes de memoria
            }
            limits = { # El máximo que el Pod puede consumir (para evitar que acapare recursos)
              cpu    = "500m" # 0.5 de un núcleo de CPU
              memory = "512Mi" # 512 Megabytes de memoria
            }
          }
          
        }
      }
    }
  }
  depends_on = [
    kubernetes_namespace.reservas_horarios_namespace,
    kubernetes_service_v1.postgres_service # Ensure Postgres is up before deploying app
  ]
}

resource "kubernetes_service_v1" "reservas_horarios_service" {
  metadata {
    name      = "reservas-horarios-service"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    labels = {
      app = "reservas-horarios"
    }
  }
  spec {
    selector = {
      app = "reservas-horarios"
    }
    port {
      port        = 80
      target_port = 8000 # Assuming your application listens on 8080
    }
    type = "ClusterIP" # Accessible only within the cluster
  }
  depends_on = [kubernetes_deployment_v1.reservas_horarios_deployment]
}