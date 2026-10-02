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
