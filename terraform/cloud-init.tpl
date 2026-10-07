#cloud-config
packages:
  - chrony
runcmd:
%{ for name, node in nodes }
  - echo "${node.private_ip} ${node.hostname}" >> /etc/hosts
%{ endfor }
  - systemctl enable --now chronyd