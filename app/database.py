import sqlite3
import os
from datetime import datetime

DB_PATH = "data/autopilot.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                tier TEXT,
                routed_model TEXT,
                cost REAL,
                latency_ms REAL,
                quality_score INTEGER,
                escalated BOOLEAN
            )
        """)

def log_request(prompt, tier, model, cost, latency):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO requests 
            (timestamp, prompt, tier, routed_model, cost, latency_ms, quality_score, escalated) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), prompt, tier, model, cost, latency, None, False)
        )
        return cursor.lastrowid

def update_evaluation(log_id, score, escalated):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE requests SET quality_score = ?, escalated = ? WHERE id = ?",
            (score, escalated, log_id)
        )