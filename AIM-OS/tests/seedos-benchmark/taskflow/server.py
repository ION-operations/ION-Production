"""Flask API server for TaskFlow."""

from flask import Flask, request, jsonify
from .models import Task
from .storage import load_tasks, save_tasks, get_task, add_task, update_task, delete_task
from .analytics import detect_anomalies, get_summary_stats


app = Flask(__name__)


@app.route("/tasks", methods=["GET"])
def list_tasks():
    """List all tasks, optionally filtered by status."""
    tasks = load_tasks()
    status_filter = request.args.get("status")
    if status_filter:
        tasks = [t for t in tasks if t.status == status_filter]
    return jsonify([t.to_dict() for t in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    
    # BUG: no input validation — accepts any garbage data
    task = Task.from_dict(data)
    add_task(task)
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_single_task(task_id):
    """Get a single task by ID."""
    task = get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_single_task(task_id):
    """Update a task."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400
    
    task = update_task(task_id, data)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_single_task(task_id):
    """Delete a task."""
    success = delete_task(task_id)
    if not success:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"message": "Task deleted"}), 200


@app.route("/analytics/anomalies", methods=["GET"])
def get_anomalies():
    """Detect duration anomalies."""
    tasks = load_tasks()
    threshold = float(request.args.get("threshold", 2.0))
    anomalies = detect_anomalies(tasks, threshold)
    return jsonify([
        {"task": t.to_dict(), "reason": reason}
        for t, reason in anomalies
    ])


@app.route("/analytics/summary", methods=["GET"])
def get_analytics_summary():
    """Get summary statistics."""
    tasks = load_tasks()
    return jsonify(get_summary_stats(tasks))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
