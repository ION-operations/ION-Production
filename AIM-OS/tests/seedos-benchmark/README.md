# TaskFlow — Lightweight Task Manager API

A small Python REST API for managing tasks with CSV-based persistence.

## Features
- CRUD operations for tasks via HTTP API
- CSV file storage backend
- Anomaly detection on task durations
- Priority-based scheduling
- Export to JSON

## Quick Start
```bash
pip install -r requirements.txt
python -m taskflow.server
```

## Project Structure
```
taskflow/
├── __init__.py
├── server.py        # Flask API endpoints
├── models.py        # Task data model
├── storage.py       # CSV read/write persistence
├── analytics.py     # Duration anomaly detection
└── scheduler.py     # Priority queue scheduler
tests/
└── test_models.py   # Unit tests
data/
└── tasks.csv        # Sample task data
```

## API Endpoints
- `GET /tasks` — list all tasks
- `POST /tasks` — create task
- `GET /tasks/<id>` — get single task
- `PUT /tasks/<id>` — update task
- `DELETE /tasks/<id>` — delete task
- `GET /analytics/anomalies` — detect duration anomalies
