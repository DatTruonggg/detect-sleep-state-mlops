
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.80.0"
    }
  }
  required_version = ">= 1.7.5"
}

provider "google" {
  credentials = ".credentials/terraform-sa.json"
  project     = var.project_id
  region      = var.region
}


resource "google_container_cluster" "primary" {
  name     = "${var.k8s}-gke"
  location = var.region
  remove_default_node_pool = true
  initial_node_count       = 1

  node_config {
    service_account = "terraform-sa@${var.project_id}.iam.gserviceaccount.com"
  }
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-standard-4" # 4 CPU and 16 GB Memory
  }
}
