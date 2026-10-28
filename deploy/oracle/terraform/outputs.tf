output "public_ip" {
  value       = oci_core_instance.reviewpilot.public_ip
  description = "SSH target for ubuntu@"
}

output "ssh_command" {
  value = "ssh -i <private_key> ubuntu@${oci_core_instance.reviewpilot.public_ip}"
}
