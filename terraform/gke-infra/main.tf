# gke-infra/main.tf

# -----------------------------------------------------------
# Google Cloud Provider Configuration
# -----------------------------------------------------------
provider "google" {
  project = "lab-reservations-465014"
  region  = "us-east1" # Use regional, or the specific zone like "us-east1-c"
  # If you use a zone here, make sure your GKE cluster also uses the same zone.
  # If you use a region here, and your GKE cluster is regional, that's fine.
}

# -----------------------------------------------------------
# Terraform Backend Configuration (for remote state in GCS)
# -----------------------------------------------------------
terraform {
  backend "gcs" {
    bucket = "terraform-state-reservas-ucab-sahili"
    prefix = "terraform/state/gke-infra" 
  }
}

# -----------------------------------------------------------
# Define Your Virtual Private Cloud (VPC) Network
# -----------------------------------------------------------
resource "google_compute_network" "lab_reservations_vpc" {
  name = "lab-reservations-vpc-network"
  auto_create_subnetworks = true
}

# -----------------------------------------------------------
# Provision Your Google Kubernetes Engine (GKE) Cluster
# -----------------------------------------------------------
resource "google_container_cluster" "primary_gke_cluster" {
  name     = "lab-reservations-cluster"
  location = "us-east1-c" 

  initial_node_count = 1
  remove_default_node_pool = true
  network    = google_compute_network.lab_reservations_vpc.name

  addons_config {
    http_load_balancing {
      disabled = false
    }
  }

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

# -----------------------------------------------------------
# Define the custom node pool for your GKE cluster
# -----------------------------------------------------------
resource "google_container_node_pool" "default_node_pool" {
  name       = "default-node-pool"
  location = "us-east1-c" 
  cluster    = google_container_cluster.primary_gke_cluster.name
  node_count = 1

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

# IMPORTANT: Output the GKE cluster endpoint and CA cert for the second config
output "gke_endpoint" {
  value = google_container_cluster.primary_gke_cluster.endpoint
  description = "GKE cluster endpoint"
}

output "gke_ca_certificate" {
  value = google_container_cluster.primary_gke_cluster.master_auth[0].cluster_ca_certificate
  description = "GKE cluster CA certificate"
}