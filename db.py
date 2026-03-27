import json
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = os.getenv("DB_PATH", "spark_feedback.db")

# Use Postgres if DATABASE_URL is set, otherwise SQLite
if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

    def _conn():
        return psycopg2.connect(DATABASE_URL)

    PH = "%s"  # Postgres placeholder

else:
    import sqlite3

    def _conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    PH = "?"  # SQLite placeholder


def init_db():
    with _conn() as conn:
        cur = conn.cursor()
        if DATABASE_URL:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    week INTEGER NOT NULL,
                    spark_name TEXT NOT NULL,
                    evaluator_key TEXT NOT NULL,
                    evaluator_name TEXT NOT NULL,
                    section TEXT NOT NULL,
                    scores TEXT NOT NULL,
                    comments TEXT NOT NULL,
                    overall_score INTEGER,
                    overall_comment TEXT,
                    submitted_at TEXT NOT NULL,
                    UNIQUE (week, spark_name, evaluator_key)
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week INTEGER NOT NULL,
                    spark_name TEXT NOT NULL,
                    evaluator_key TEXT NOT NULL,
                    evaluator_name TEXT NOT NULL,
                    section TEXT NOT NULL,
                    scores TEXT NOT NULL,
                    comments TEXT NOT NULL,
                    overall_score INTEGER,
                    overall_comment TEXT,
                    submitted_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_feedback_unique
                ON feedback(week, spark_name, evaluator_key)
            """)
        conn.commit()
    print("Database initialised.")


def save_feedback(week, spark_name, evaluator_key, evaluator_name, section,
                  scores, comments, overall_score=None, overall_comment=None):
    with _conn() as conn:
        cur = conn.cursor()
        if DATABASE_URL:
            cur.execute(f"""
                INSERT INTO feedback
                  (week, spark_name, evaluator_key, evaluator_name, section,
                   scores, comments, overall_score, overall_comment, submitted_at)
                VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH})
                ON CONFLICT (week, spark_name, evaluator_key) DO UPDATE SET
                  evaluator_name=EXCLUDED.evaluator_name,
                  section=EXCLUDED.section,
                  scores=EXCLUDED.scores,
                  comments=EXCLUDED.comments,
                  overall_score=EXCLUDED.overall_score,
                  overall_comment=EXCLUDED.overall_comment,
                  submitted_at=EXCLUDED.submitted_at
            """, (
                week, spark_name, evaluator_key, evaluator_name, section,
                json.dumps(scores), json.dumps(comments),
                overall_score, overall_comment,
                datetime.utcnow().isoformat(),
            ))
        else:
            cur.execute(f"""
                INSERT OR REPLACE INTO feedback
                  (week, spark_name, evaluator_key, evaluator_name, section,
                   scores, comments, overall_score, overall_comment, submitted_at)
                VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH})
            """, (
                week, spark_name, evaluator_key, evaluator_name, section,
                json.dumps(scores), json.dumps(comments),
                overall_score, overall_comment,
                datetime.utcnow().isoformat(),
            ))
        conn.commit()


def get_feedback(week, spark_name=None, section=None):
    with _conn() as conn:
        if DATABASE_URL:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
        query = f"SELECT * FROM feedback WHERE week = {PH}"
        params = [week]
        if spark_name:
            query += f" AND spark_name = {PH}"
            params.append(spark_name)
        if section:
            query += f" AND section = {PH}"
            params.append(section)
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def has_submitted(week, spark_name, evaluator_key):
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT id FROM feedback WHERE week={PH} AND spark_name={PH} AND evaluator_key={PH}",
            (week, spark_name, evaluator_key),
        )
        return cur.fetchone() is not None
