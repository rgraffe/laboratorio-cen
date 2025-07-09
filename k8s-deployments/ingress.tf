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
      "nginx.ingress.kubernetes.io/rewrite-target": "/$2"
    }
  }
  spec {
    rule {
      http {
        # --- REGLA MODIFICADA PARA EL SERVICIO DE RESERVAS ---
        path {
          path = "/api/reservas(/|$)(.*)" 
          path_type = "ImplementationSpecific" 
          backend {
            service {
              name = kubernetes_service_v1.reservas_horarios_service.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }

        # --- REGLA PARA EL SERVICIO DE LABORATORIOS  ---
        path {
          path = "/api/laboratorios(/|$)(.*)"
          path_type = "ImplementationSpecific" 
          backend {
            service {
              name = kubernetes_service_v1.laboratorios_service.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }

        # --- REGLA PARA EL SERVICIO DE AUTENTICACIÓN  ---
        path {
          path = "/api/auth(/|$)(.*)"
          path_type = "ImplementationSpecific" 
          backend {
            service {
              name = kubernetes_service_v1.auth_service.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
        # ----------------------------------------------------

      }
    }
  }
  depends_on = [
    kubernetes_service_v1.reservas_horarios_service,
    kubernetes_service_v1.laboratorios_service,
    kubernetes_service_v1.auth_service,
    helm_release.nginx_ingress_controller
  ]
}