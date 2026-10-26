import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "recallmap.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(name, subject)
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS recall_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
            score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 5),
            attempted_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS topic_links (
            source_topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            target_topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            relationship TEXT NOT NULL DEFAULT 'related',
            PRIMARY KEY(source_topic_id, target_topic_id),
            CHECK(source_topic_id <> target_topic_id)
        );
        CREATE INDEX IF NOT EXISTS idx_notes_topic ON notes(topic_id);
        CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_question ON recall_attempts(question_id);
        """)


def query_df(sql, params=()):
    import pandas as pd
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def list_topics():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM topics ORDER BY subject, name").fetchall()


def add_topic(name, subject):
    name, subject = name.strip(), subject.strip()
    if not name or not subject:
        raise ValueError("Topic and subject are required.")
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO topics(name, subject) VALUES (?, ?)", (name, subject))


def add_note(topic_id, title, content):
    if not title.strip() or not content.strip():
        raise ValueError("A title and note content are required.")
    with get_connection() as conn:
        conn.execute("INSERT INTO notes(topic_id, title, content) VALUES (?, ?, ?)",
                     (int(topic_id), title.strip(), content.strip()))


def add_question(topic_id, question, answer):
    if not question.strip() or not answer.strip():
        raise ValueError("Both question and answer are required.")
    with get_connection() as conn:
        conn.execute("INSERT INTO questions(topic_id, question, answer) VALUES (?, ?, ?)",
                     (int(topic_id), question.strip(), answer.strip()))


def save_attempt(question_id, score):
    if not 0 <= int(score) <= 5:
        raise ValueError("Score must be between 0 and 5.")
    with get_connection() as conn:
        conn.execute("INSERT INTO recall_attempts(question_id, score) VALUES (?, ?)",
                     (int(question_id), int(score)))


def delete_note(note_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (int(note_id),))


def delete_question(question_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM questions WHERE id = ?", (int(question_id),))


def add_topic_link(source_id, target_id, relationship="related"):
    if int(source_id) == int(target_id):
        raise ValueError("Choose two different topics.")
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO topic_links(source_topic_id, target_topic_id, relationship) VALUES (?, ?, ?)",
                     (int(source_id), int(target_id), relationship.strip() or "related"))
