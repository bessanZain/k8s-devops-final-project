from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import DEFAULT_PRIORITY, PRIORITIES, Task

bp = Blueprint("main", __name__)

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _error(message, status):
    return jsonify(error=message), status


# ---------- health checks ----------
@bp.get("/health")
def health():
    """Liveness: the process is running (no database check)."""
    return jsonify(status="ok")


@bp.get("/ready")
def ready():
    """Readiness: the app can reach its database."""
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return _error("database not reachable", 503)
    return jsonify(status="ready")


@bp.get("/version")
def version():
    return jsonify(version=current_app.config["APP_VERSION"])


# ---------- REST API ----------
@bp.get("/api/tasks")
def list_tasks():
    stmt = db.select(Task).order_by(Task.id)
    priority = request.args.get("priority")
    if priority:
        stmt = stmt.where(Task.priority == priority)
    return jsonify([task.to_dict() for task in db.session.scalars(stmt)])


@bp.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "").strip()
    priority = data.get("priority", DEFAULT_PRIORITY)
    if not title:
        return _error("title is required", 400)
    if priority not in PRIORITIES:
        return _error("priority must be one of: " + ", ".join(PRIORITIES), 400)
    task = Task(
        title=title[:120],
        description=str(data.get("description") or ""),
        priority=priority,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@bp.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return _error("task not found", 404)
    return jsonify(task.to_dict())


@bp.put("/api/tasks/<int:task_id>")
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return _error("task not found", 404)
    data = request.get_json(silent=True) or {}
    if "priority" in data:
        if data["priority"] not in PRIORITIES:
            return _error("priority must be one of: " + ", ".join(PRIORITIES), 400)
        task.priority = data["priority"]
    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return _error("title must not be empty", 400)
        task.title = title[:120]
    if "description" in data:
        task.description = str(data["description"])
    if "done" in data:
        task.done = bool(data["done"])
    db.session.commit()
    return jsonify(task.to_dict())


@bp.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return _error("task not found", 404)
    db.session.delete(task)
    db.session.commit()
    return "", 204


# ---------- web UI ----------
@bp.get("/")
def index():
    tasks = list(db.session.scalars(db.select(Task)))
    tasks.sort(key=lambda t: (t.done, PRIORITY_ORDER.get(t.priority, 1), t.id))
    return render_template(
        "index.html",
        tasks=tasks,
        priorities=PRIORITIES,
        default_priority=DEFAULT_PRIORITY,
        version=current_app.config["APP_VERSION"],
    )


@bp.post("/tasks")
def create_task_form():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", DEFAULT_PRIORITY)
    if title and priority in PRIORITIES:
        db.session.add(
            Task(
                title=title[:120],
                description=request.form.get("description", "").strip(),
                priority=priority,
            )
        )
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    if task is not None:
        task.done = not task.done
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_task_form(task_id):
    task = db.session.get(Task, task_id)
    if task is not None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("main.index"))
