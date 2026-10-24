variable "region" {
  description = "OCI region, e.g. eu-frankfurt-1"
  type        = string
}

variable "tenancy_ocid" {
  type = string
}

variable "user_ocid" {
  type = string
}

variable "fingerprint" {
  type = string
}

variable "private_key_path" {
  type        = string
  description = "Path to OCI API private key PEM"
}

variable "compartment_id" {
  type        = string
  description = "Compartment for resources (often tenancy OCID for root)"
}

variable "ssh_public_key" {
  type        = string
  description = "OpenSSH public key for ubuntu user"
}

variable "instance_display_name" {
  type    = string
  default = "reviewpilot-bot"
}

variable "ocpus" {
  type    = number
  default = 2
}

variable "memory_in_gbs" {
  type    = number
  default = 12
}

variable "git_ref" {
  type    = string
  default = "main"
}
