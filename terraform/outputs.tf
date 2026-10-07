output "public_ips" {
  description = "Public IP address of each node"
  value       = { for name, ip in azurerm_public_ip.node : name => ip.ip_address }
}

output "private_ips" {
  description = "Private IP address of each node"
  value       = { for name, node in var.nodes : name => node.private_ip }
}

output "ssh_commands" {
  description = "Ready-to-use SSH command for each node"
  value = {
    for name, ip in azurerm_public_ip.node :
    name => "ssh -i ${trimsuffix(var.ssh_public_key_path, ".pub")} ${var.admin_username}@${ip.ip_address}"
  }
}