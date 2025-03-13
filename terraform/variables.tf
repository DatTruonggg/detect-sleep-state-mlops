variable "project_id" {
  description = "The project ID of the cluster"
  default     = "spring-house-449810-s4"
}

variable "region" {
  description = "The region the cluster in"
  default     = "asia-southeast1-a"
}

variable "k8s" {
  description = "Kubernetes cluster for detect sleep state system"
  default     = "detect-sleep-state"
}