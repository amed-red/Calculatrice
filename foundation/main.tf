terraform {
  required_providers {
    scaleway = {
      source = "scaleway/scaleway"
    }
  }
  required_version = ">= 0.13"
}

variable "env" {
  type        = string
  description = "Environment name (dev or prod)"
}

variable "chegueni-ouadid-benabdelaziz" {
  type        = string
  description = "chegueni-ouadid-benabdelaziz"
  default     = "chegueni-ouadid-benabdelaziz"
}

provider "scaleway" {
  zone   = "fr-par-1"
  region = "fr-par"
}

# 1. Container Registry (Unique for the project)
resource "scaleway_registry_namespace" "main" {
  name        = "registry-${var.chegueni-ouadid-benabdelaziz}"
  description = "Container registry for the cloud native calculator"
  is_public   = false
}

# 2. Kubernetes Cluster (Unique for the project)
resource "scaleway_k8s_cluster" "main" {
  name                        = "cluster-${var.chegueni-ouadid-benabdelaziz}"
  version                     = "1.28.2"
  cni                         = "cilium"
  delete_additional_resources = false
}

resource "scaleway_k8s_pool" "main" {
  cluster_id = scaleway_k8s_cluster.main.id
  name       = "pool-${var.chegueni-ouadid-benabdelaziz}"
  node_type  = "DEV1-M"
  size       = 3
}

# 3. Databases (One for each environment)
resource "scaleway_rdb_instance" "database" {
  name           = "db-${var.env}-${var.chegueni-ouadid-benabdelaziz}"
  node_type      = "DB-DEV-S"
  engine         = "PostgreSQL-15"
  is_ha_cluster  = false
  disable_backup = true
}

# 4. LoadBalancers (One for each environment)
resource "scaleway_lb" "base" {
  name = "lb-${var.env}-${var.chegueni-ouadid-benabdelaziz}"
  type = "LB-S"
}

# 5. DNS Entries (One for each environment)
resource "scaleway_domain_record" "dns" {
  dns_zone = "polytech-dijon.kiowy.net"
  name     = var.env == "prod" ? "calculatrice-${var.chegueni-ouadid-benabdelaziz}" : "calculatrice-dev-${var.chegueni-ouadid-benabdelaziz}"
  type     = "A"
  data     = scaleway_lb.base.ip_address
  ttl      = 3600
}
