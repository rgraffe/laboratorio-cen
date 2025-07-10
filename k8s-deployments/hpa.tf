# k8s-deployments/hpa.tf

resource "kubernetes_horizontal_pod_autoscaler_v1" "reservas_horarios_hpa" {
  metadata {
    name      = "reservas-horarios-hpa"
    namespace = kubernetes_namespace.reservas_horarios_namespace.metadata[0].name
  }
  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment_v1.reservas_horarios_deployment.metadata[0].name
    }
    min_replicas = 1 # Mínimo de réplicas que siempre habrá
    max_replicas = 5 # Máximo de réplicas a las que puede escalar

    target_cpu_utilization_percentage = 70 # Escala si el uso promedio de CPU supera el 70% de los 'requests'
  }
  depends_on = [kubernetes_deployment_v1.reservas_horarios_deployment]
}