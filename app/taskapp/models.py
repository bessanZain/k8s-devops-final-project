from datetime import datetime, timezone

from . import db

PRIORITIES = ("low", "medium", "high")
DEFAULT_PRIORITY = "medium"


def _now():
    return datetime.now(timezone.utc)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    done = db.Column(db.Boolean, nullable=False, default=False)
    priority = db.Column(db.String(10), nullable=False, default=DEFAULT_PRIORITY)
    created_at = db.Column(db.DateTime, nullable=False, default=_now)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }
