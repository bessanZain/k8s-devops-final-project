resource "azurerm_public_ip" "node" {
  for_each            = var.nodes
  name                = "${each.value.hostname}-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "node" {
  for_each            = var.nodes
  name                = "${each.value.hostname}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.nodes.id
    private_ip_address_allocation = "Static"
    private_ip_address            = each.value.private_ip
    public_ip_address_id          = azurerm_public_ip.node[each.key].id
  }
}

resource "azurerm_linux_virtual_machine" "node" {
  for_each                        = var.nodes
  name                            = each.value.hostname
  computer_name                   = each.value.hostname
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  size                            = var.vm_size
  admin_username                  = var.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.node[each.key].id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 64
  }

  source_image_reference {
    publisher = "resf"
    offer     = "rockylinux-x86_64"
    sku       = "9-base"
    version   = "latest"
  }

  plan {
    name      = "9-base"
    product   = "rockylinux-x86_64"
    publisher = "resf"
  }

  custom_data = base64encode(templatefile("${path.module}/cloud-init.tpl", {
    nodes = var.nodes
  }))
}