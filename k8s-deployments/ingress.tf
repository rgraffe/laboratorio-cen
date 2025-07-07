# k8s-deployments/main.tf (or create a new ingress.tf file)

resource "kubernetes_ingress_v1" "reservas_horarios_ingress" {
  metadata {
    name      = "reservas-horarios-ingress"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
    annotations = {
      # This annotation is crucial for the NGINX Ingress Controller to manage this Ingress
      "kubernetes.io/ingress.class": "nginx"
      # === Anotaciones para Rate Limiting por IP ===
      "nginx.ingress.kubernetes.io/limit-rps": "2"       # Límite de 2 solicitudes por segundo
      "nginx.ingress.kubernetes.io/limit-burst": "5"     # Permite ráfagas de hasta 5 solicitudes
      "nginx.ingress.kubernetes.io/limit-status-code": "429" # Código de respuesta cuando se excede el límite
      # Opcional: si quieres una clave diferente para el límite (por defecto es IP)
      # "nginx.ingress.kubernetes.io/limit-by-key": "$binary_remote_addr"
      # ==============================================
    }
  }
  spec {
    rule {
      http {
        path {
          path = "/"
          path_type = "Prefix" # This means any path starting with /
          backend {
            service {
              name = kubernetes_service_v1.reservas_horarios_service.metadata[0].name
              port {
                number = 80 # This is the service port for your reservas-horarios-service
              }
            }
          }
        }
      }
    }
    # If you have multiple services, you can define more rules here.
    # Optionally, you can also define default_backend for 404s if no rule matches.
  }
  depends_on = [
    kubernetes_service_v1.reservas_horarios_service,
    helm_release.nginx_ingress_controller # Ensure ingress controller is ready
  ]
}