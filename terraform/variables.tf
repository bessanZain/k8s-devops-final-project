variable "subscription_id" {
  description = "Azure subscription ID to deploy into"
  type        = string
}

variable "my_public_ip" {
  description = "Source address range allowed to reach SSH and the Kubernetes API, in CIDR notation (for example 203.0.113.10/32 for a single address)."
  type        = string

  validation {
    condition     = can(cidrhost(var.my_public_ip, 0))
    error_message = "my_public_ip must be CIDR notation, for example 203.0.113.10/32 or 203.0.113.0/24."
  }
}

variable "location" {

  description = "Azure region to deploy into"
  type        = string
  default     = "swedencentral"

}

variable "resource_group_name" {

  description = "Name of the resource group that holds everything"
  type        = string
  default     = "k8slab-rg"

}

variable "vnet_cidr" {
  description = "Address range of the virtual network"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vnet_cidr, 0))
    error_message = "vnet_cidr must be valid CIDR notation, for example 10.0.0.0/16."
  }
}

variable "subnet_cidr" {
  description = "Address range of the subnet that holds the nodes"
  type        = string
  default     = "10.0.1.0/24"

  validation {
    condition     = can(cidrhost(var.subnet_cidr, 0))
    error_message = "subnet_cidr must be valid CIDR notation, for example 10.0.1.0/24."
  }
}

variable "vm_size" {
  description = "Azure VM size (2 vCPU, 4 GB RAM meets the project minimum)"
  type        = string
  default     = "Standard_B2ls_v2"
}

variable "admin_username" {
  description = "Initial admin user created on each VM by Azure"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path to the public SSH key that will be installed on the VMs"
  type        = string
  default     = "~/.ssh/k8slab_key.pub"
}

variable "nodes" {
  description = "Cluster nodes. One VM is created for each entry."
  type = map(object({
    hostname   = string
    private_ip = string
  }))
  default = {
    cp1 = { hostname = "k8slab-cp1", private_ip = "10.0.1.10" }
    w1  = { hostname = "k8slab-w1", private_ip = "10.0.1.11" }
  }
}
