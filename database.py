import sqlite3
import hashlib
from typing import Optional

DB_PATH = "bot_data.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            pvm_points INTEGER DEFAULT 0,
            community_points INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            image_hash TEXT NOT NULL,
            players TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            reviewed_by INTEGER,
            pvm_points INTEGER DEFAULT 0,
            participant_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            submissions_channel_id INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value INTEGER NOT NULL
        )
    """)

    c.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_image_hash ON submissions(image_hash)
    """)

    migrations = [
        ("submissions", "participant_ids", "TEXT DEFAULT ''"),
        ("submissions", "review_message_id", "INTEGER"),
        ("submissions", "channel_id", "INTEGER"),
    ]
    for table, column, definition in migrations:
        existing = [r["name"] for r in c.execute(f"PRAGMA table_info({table})")]
        if column not in existing:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    conn.commit()
    conn.close()


def compute_image_hash(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


def player_exists(user_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM players WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


def add_player(user_id: int, username: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
        (user_id, username),
    )
    added = c.rowcount > 0
    conn.commit()
    conn.close()
    return added


def remove_player(user_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_player(user_id: int) -> Optional[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_players() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM players ORDER BY pvm_points + community_points DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_pvm_points(user_id: int, points: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE players SET pvm_points = pvm_points + ? WHERE user_id = ?",
        (points, user_id),
    )
    conn.commit()
    conn.close()


def add_community_points(user_id: int, points: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE players SET community_points = community_points + ? WHERE user_id = ?",
        (points, user_id),
    )
    conn.commit()
    conn.close()


def set_community_points(user_id: int, points: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE players SET community_points = ? WHERE user_id = ?",
        (points, user_id),
    )
    conn.commit()
    conn.close()


def set_pvm_points(user_id: int, points: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE players SET pvm_points = ? WHERE user_id = ?",
        (points, user_id),
    )
    conn.commit()
    conn.close()


def image_already_submitted(image_hash: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM submissions WHERE image_hash = ? AND status != 'denied'",
        (image_hash,),
    )
    result = c.fetchone()
    conn.close()
    return result is not None


def create_submission(
    user_id: int,
    image_url: str,
    image_hash: str,
    players: str,
    participant_ids: list[int] | None = None,
    review_message_id: int | None = None,
    channel_id: int | None = None,
) -> int:
    conn = get_connection()
    c = conn.cursor()
    ids_str = ",".join(str(i) for i in (participant_ids or []))
    c.execute(
        """INSERT INTO submissions
           (user_id, image_url, image_hash, players, participant_ids, review_message_id, channel_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, image_url, image_hash, players, ids_str, review_message_id, channel_id),
    )
    sub_id = c.lastrowid
    conn.commit()
    conn.close()
    return sub_id


def get_submission(sub_id: int) -> Optional[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM submissions WHERE id = ?", (sub_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_pending_submissions() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM submissions WHERE status = 'pending' ORDER BY created_at ASC"
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_submissions() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_submission_status(sub_id: int, status: str, reviewed_by: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE submissions SET status = ?, reviewed_by = ? WHERE id = ?",
        (status, reviewed_by, sub_id),
    )
    conn.commit()
    conn.close()


def set_submissions_channel(guild_id: int, channel_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO settings (guild_id, submissions_channel_id) VALUES (?, ?)",
        (guild_id, channel_id),
    )
    conn.commit()
    conn.close()


def get_submissions_channel(guild_id: int) -> Optional[int]:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT submissions_channel_id FROM settings WHERE guild_id = ?",
        (guild_id,),
    )
    row = c.fetchone()
    conn.close()
    return row["submissions_channel_id"] if row else None


def add_item(name: str, value: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO items (name, value) VALUES (?, ?)", (name, value))
    conn.commit()
    conn.close()


def remove_item(name: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE name = ?", (name,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_item(name: str) -> Optional[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_items() -> list[dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY name ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
