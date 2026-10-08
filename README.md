# k8s-devops-final-project

DevOps Bootcamp final capstone: Terraform, Ansible, Kubernetes, and CI/CD.

(Full documentation will be added as the project progresses.)

## Task 1: Repository & Git Hygiene

**Q1. Which files did you exclude with .gitignore, and what sensitive data would they leak if committed?**

- `*.tfstate*`: Terraform state. It records all created resources and can contain secrets (IPs, keys, passwords) in plain text.
- `.terraform/`: provider plugins and working files. Large and regenerable, and not source code.
- `terraform.tfvars`: real variable values, such as my Azure subscription ID and my public IP.
- Private SSH keys (`k8slab_key`, `id_ed25519`, `*.pem`): they would give anyone full access to my VMs.
- `kubeconfig` / `admin.conf`: they contain cluster credentials, so anyone with them has admin control of the Kubernetes cluster.

**Q2. If a secret is committed and deleted in a later commit, is it safe?**

No. Git keeps the full history, so the secret still exists in the earlier commit and can be recovered by anyone who clones the repo. On a public repo, bots also scan for leaked keys within minutes. The secret must be treated as compromised and rotated (a new key or password), and the history cleaned if needed. Prevention (a `.gitignore` from the first commit) is much better than cleanup.

## Task 2: Workstation Tool Verification

**Q. How does Terraform authenticate to Azure in this setup, and why is this method safer than hardcoding credentials inside .tf files?**

Terraform's `azurerm` provider reuses my Azure CLI session. I sign in once with `az login` (including MFA), and Terraform picks up that login automatically, so no password or key appears in any `.tf` file. Only the subscription ID is passed, through a variable. This is safer because:
- no secret exists in the code, so nothing can be leaked through Git (my repo is public);
- the login token is temporary and tied to my verified sign-in, and it can be revoked;
- hardcoded credentials would be copied into every clone, commit, and backup of the repo.
## Task 3: Azure Subscription Setup

**Q. What happens if you run `terraform apply` before accepting marketplace terms?**

The apply fails when it reaches the VM creation. Azure refuses to deploy a Marketplace image (Rocky Linux from publisher `resf`) until the legal terms are accepted on the subscription, and the error says the legal terms have not been accepted. Terraform may already have created the network resources by then, so the deployment ends up half-built. The fix is to accept the terms (`az vm image terms accept ...`) and run `terraform apply` again. Accepting them once, before the first apply, avoids the failed run.

## Task 4: Dedicated SSH Key Pair

**Q. What is the difference between a public key and a private key, and where does each reside?**

An SSH key pair has two mathematically linked parts. The **public key** (`k8slab_key.pub`) is like a lock: it can be shared freely and is placed on the servers I want to access (in `~/.ssh/authorized_keys` on each VM). The **private key** (`k8slab_key`) is the matching key that opens it: it never leaves my laptop and must never be shared or committed to Git. When I connect, the server challenges me, and only the holder of the private key can answer correctly, so no password is sent over the network.

**Q. Why does the NSG not need rules for Kubernetes traffic between cp1 and w1 inside the subnet?**

Every Azure NSG includes default rules, and one of them (`AllowVnetInBound`) allows all traffic between resources in the same virtual network. Both nodes are in the same subnet inside the VNet, so Kubernetes traffic between them (the API on 6443, the kubelet on 10250, and the Calico networking ports) is already permitted. The NSG rules I wrote only control traffic coming from outside: SSH and the API from my IP, and the app ports from the internet.

## Task 5: Terraform Infrastructure Code

**Q1. Why does the NSG not need rules for Kubernetes traffic between cp1 and w1 inside the subnet?**

Every Azure NSG includes default rules, and one of them (`AllowVnetInBound`) allows all traffic between resources in the same virtual network. Both nodes are in the same subnet inside the VNet, so Kubernetes traffic between them (the API on 6443, the kubelet on 10250, and the Calico networking ports) is already permitted. The NSG rules I wrote only control traffic coming from outside: SSH and the API from my network, and the app ports from the internet.

**Q2. Why must the private IPs be static for this cluster?**

Many things record the nodes' private addresses: the `/etc/hosts` entries written by cloud-init, the Ansible variables (`cp1_ip`, `w1_ip`), and the Kubernetes control plane, which advertises its address and puts it in its certificates and in the join command. If an address changed after a restart, those references would point to the wrong machine and the cluster would break. Static IPs keep them stable.

**Q3. What is stored in `terraform.tfstate`, and why must it never be pushed to Git?**

The state file maps my code to the real resources Terraform created. It holds every resource's attributes, such as IDs, IP addresses, and configuration, and it can contain sensitive values in plain text. It must never go to Git, especially a public repo, because it would reveal my infrastructure and any secrets inside it. Sharing it can also cause conflicts, since it must always match the real environment.

**Deviation from the brief (firewall source):** the assignment says SSH (22) and the Kubernetes API (6443) should be allowed only from my public IP. My ISP routes traffic through a pool of public addresses (I observed .93, .94, .95 and .80 within a day, and different "what is my IP" sites reported different ones), so a single-address rule kept blocking me. I allowed my ISP's `/24` range instead (`165.16.83.0/24`). SSH still requires my private key, because password login is disabled on the VMs.