"""SQLite audit trail for agent runs and tool actions."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "data" / "workpilot.db"

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        final_result TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        detail TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES runs(run_id)
    )""")
    return conn

def start_run(task):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute("INSERT INTO runs(task,status,started_at) VALUES(?,?,?)",
                           (task, "running", now))
        return cur.lastrowid

def log_event(run_id, event_type, detail):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute("INSERT INTO events(run_id,event_type,detail,created_at) VALUES(?,?,?,?)",
                     (run_id, event_type, json.dumps(detail, ensure_ascii=False), now))

def finish_run(run_id, status, result):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute("UPDATE runs SET status=?,finished_at=?,final_result=? WHERE run_id=?",
                     (status, now, json.dumps(result, ensure_ascii=False), run_id))

def recent_runs(limit=20):
    with _connect() as conn:
        rows = conn.execute("SELECT run_id,task,status,started_at,finished_at FROM runs ORDER BY run_id DESC LIMIT ?",
                            (limit,)).fetchall()
    return [{"run_id": r[0], "task": r[1], "status": r[2], "started_at": r[3], "finished_at": r[4]}
            for r in rows]
