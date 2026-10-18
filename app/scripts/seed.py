"""Populate the database with 10 sample tasks (safe to run more than once)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from taskapp import create_app, db  # noqa: E402
from taskapp.models import Task  # noqa: E402

SAMPLE_TASKS = [
    ("Provision the Azure infrastructure", "Network, NSG and two Rocky Linux VMs", "high"),
    ("Configure nodes with Ansible", "Packages, chrony and sshd on both nodes", "high"),
    ("Bootstrap the Kubernetes cluster", "kubeadm, containerd and Calico", "high"),
    ("Write unit tests", "Cover the priority field", "medium"),
    ("Containerize the application", "Dockerfile and docker-compose", "medium"),
    ("Build the CI/CD pipeline", "Lint, test and push to GHCR", "medium"),
    ("Deploy PostgreSQL on Kubernetes", "Deployment, Service, Secret and PVC", "medium"),
    ("Write the README", "Answers and post-mortems", "low"),
    ("Take the screenshots", "One per deliverable", "low"),
    ("Destroy the cloud resources", "terraform destroy at the end", "low"),
]


def seed():
    app = create_app()
    inserted = 0
    with app.app_context():
        for title, description, priority in SAMPLE_TASKS:
            if db.session.scalar(db.select(Task).where(Task.title == title)) is None:
                db.session.add(Task(title=title, description=description, priority=priority))
                inserted += 1
        db.session.commit()
    print(f"Inserted {inserted} new tasks ({len(SAMPLE_TASKS)} samples defined).")


if __name__ == "__main__":
    seed()
