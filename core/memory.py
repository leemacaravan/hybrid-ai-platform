import sqlite3
from datetime import datetime

DB_PATH = "./memory.db"

def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Career side: track interview weak spots
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            question TEXT,
            correct INTEGER,
            timestamp TEXT
        )
    """)
    # Missing persons side: track case updates
    c.execute("""
        CREATE TABLE IF NOT EXISTS case_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            event TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Memory DB initialized")

def log_quiz_result(topic: str, question: str, correct: bool):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO quiz_results (topic, question, correct, timestamp) VALUES (?, ?, ?, ?)",
              (topic, question, int(correct), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_weak_topics(limit: int = 5) -> list[str]:
    """Return topics with the most wrong answers — used to bias agents."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT topic, SUM(1 - correct) as wrong_count
        FROM quiz_results
        GROUP BY topic
        ORDER BY wrong_count DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def log_case_event(case_id: str, event: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO case_log (case_id, event, timestamp) VALUES (?, ?, ?)",
              (case_id, event, datetime.now().isoformat()))
    conn.commit()
    conn.close()