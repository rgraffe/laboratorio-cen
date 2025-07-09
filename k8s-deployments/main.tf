# k8s-deployments/main.tf

# -----------------------------------------------------------
# Google Cloud Provider (minimal, just for gcloud client config)
# -----------------------------------------------------------
provider "google" {
  project = "lab-reservations-465014"
  # No need for region/zone here unless you have other Google Cloud resources
  # that are NOT Kubernetes resources (e.g., custom compute instances not in GKE)
}

# -----------------------------------------------------------
# Terraform Backend Configuration (for remote state in GCS)
# -----------------------------------------------------------
terraform {
  backend "gcs" {
    bucket = "terraform-state-reservas-ucab-sahili"
    prefix = "terraform/state/k8s-deployments" # <-- IMPORTANT: Different prefix for this state file
  }
}

# -----------------------------------------------------------
# Data source to get the access token from the gcloud environment.
# -----------------------------------------------------------
data "google_client_config" "default" {}

# -----------------------------------------------------------
# Proveedores para Kubernetes y Helm (using data sources for GKE cluster info)
# -----------------------------------------------------------

# Fetch existing GKE cluster information using a data source
# This allows Terraform to get the endpoint and CA certificate of the
# cluster that was created by the 'gke-infra' configuration.
data "google_container_cluster" "existing_gke_cluster" {
  name     = "lab-reservations-cluster"
  location = "us-east1-c" # <-- IMPORTANT: MUST match the location used in gke-infra/main.tf
}

# Proveedor Kubernetes: Configura cómo Terraform se conecta a tu clúster de GKE.
# This uses the access token from the gcloud environment for robust authentication
# and the GKE cluster details fetched above.
provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.existing_gke_cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(data.google_container_cluster.existing_gke_cluster.master_auth[0].cluster_ca_certificate)
}

# Proveedor Helm: Le dice a Terraform cómo instalar Helm Charts en Kubernetes.
provider "helm" {
  # Explicitly configure the Helm provider to use the same credentials as the Kubernetes provider.
  # This ensures it can connect to the GKE cluster to install charts.
  kubernetes = {
    host                   = "https://${data.google_container_cluster.existing_gke_cluster.endpoint}"
    token                  = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(data.google_container_cluster.existing_gke_cluster.master_auth[0].cluster_ca_certificate)
  }
}

# -----------------------------------------------------------
# Define un Namespace centralizado para todos los microservicios de la aplicación.
# -----------------------------------------------------------

# Este Namespace alojará los servicios de reservas-horarios, laboratorios y autenticación,
# incluyendo sus respectivas bases de datos.
resource "kubernetes_namespace" "reservas_horarios_namespace" {
  metadata {
    name = "reservas-horarios-app"
  }
}
# -----------------------------------------------------------
# Despliegue de Nginx Ingress Controller usando Helm
# -----------------------------------------------------------

# Define un Namespace específico para el Ingress Controller.
resource "kubernetes_namespace" "ingress_nginx_namespace" {
  metadata {
    name = "ingress-nginx"
  }
}

# Despliega el Nginx Ingress Controller usando su Helm chart oficial.
resource "helm_release" "nginx_ingress_controller" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx" # Repositorio oficial del chart
  chart      = "ingress-nginx"                               # Nombre del chart
  namespace  = kubernetes_namespace.ingress_nginx_namespace.metadata[0].name # Instalar en el Namespace creado

  # Configuración para el chart, usando yamlencode para mayor claridad y validación de sintaxis.
  values = [
    yamlencode({
      controller = {
        service = {
          type = "LoadBalancer" # Solicita un balanceador de carga externo a GCP
        }
        replicaCount = 2 # Número de réplicas para el Ingress Controller
      }
    })
  ]

  # Asegura que el Namespace exista antes de intentar desplegar el Helm Release.
  depends_on = [kubernetes_namespace.ingress_nginx_namespace]
}

# -----------------------------------------------------------
# Obtener la IP externa del LoadBalancer del Nginx Ingress Controller
# -----------------------------------------------------------

# Este 'data' block leerá el servicio Kubernetes del Ingress Controller
# para obtener su estado, incluyendo la IP externa asignada por GCP.
data "kubernetes_service" "ingress_nginx_loadbalancer" {
  metadata {
    name      = "ingress-nginx-controller" # Nombre por defecto del servicio LoadBalancer del Nginx Ingress
    namespace = kubernetes_namespace.ingress_nginx_namespace.metadata[0].name
  }
  # Asegura que el Helm Release se haya completado y el servicio exista antes de intentar leerlo.
  depends_on = [helm_release.nginx_ingress_controller]
}

# Muestra la IP externa del LoadBalancer como una salida de Terraform.
output "ingress_ip_address" {
  value = data.kubernetes_service.ingress_nginx_loadbalancer.status[0].load_balancer[0].ingress[0].ip
  description = "The external IP address of the Nginx Ingress LoadBalancer."
  # Asegura que el 'data' block haya sido leído exitosamente antes de intentar acceder a su valor.
  depends_on = [data.kubernetes_service.ingress_nginx_loadbalancer]
}

