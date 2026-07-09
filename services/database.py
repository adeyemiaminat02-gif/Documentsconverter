import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.config import DATABASE_URL

def init_db() -> None:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        created_at TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        default_output_format TEXT DEFAULT 'PDF',
        filename_format TEXT DEFAULT 'original',
        keep_original DEFAULT 'Yes',
        zip_batch DEFAULT 'Yes',
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversion_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        original_filename TEXT,
        source_format TEXT,
        target_format TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()

def add_user(user_id: int, username: Optional[str], first_name: str) -> None:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, first_name, now)
    )
    cursor.execute(
        "INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()

def get_settings(user_id: int) -> Dict[str, Any]:
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"default_output_format": "PDF", "filename_format": "original", "keep_original": "Yes", "zip_batch": "Yes"}

def update_setting(user_id: int, key: str, value: str) -> None:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    valid_keys = ["default_output_format", "filename_format", "keep_original", "zip_batch"]
    if key in valid_keys:
        cursor.execute(f"UPDATE user_settings SET {key} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()
    conn.close()

def add_history(user_id: int, filename: str, src: str, target: str) -> None:
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO conversion_history (user_id, original_filename, source_format, target_format, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, filename, src.upper(), target.upper(), now)
    )
    conn.commit()
    conn.close()

def get_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT original_filename, source_format, target_format, timestamp FROM conversion_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
