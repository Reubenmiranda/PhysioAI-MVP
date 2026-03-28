"""
Database utility module for PhysioAI.

Manages SQLite database connection and initialization.
"""

import sqlite3
from pathlib import Path
from typing import Optional


# Database path: backend/physioai.db
DB_PATH = Path(__file__).parent / "physioai.db"


def get_db() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn


def init_db() -> None:
    """
    Initialize the database with required tables.
    
    Creates the users table if it doesn't exist.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"[DB] Database initialized at {DB_PATH}")


def get_user_by_username(username: str) -> Optional[dict]:
    """
    Retrieve a user by username.
    
    Args:
        username: Username to search for
        
    Returns:
        dict with user data if found, None otherwise
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "username": row["username"],
            "password_hash": row["password_hash"]
        }
    return None


def create_user(username: str, password_hash: str) -> int:
    """
    Create a new user in the database.
    
    Args:
        username: Username (must be unique)
        password_hash: Hashed password (never store raw passwords)
        
    Returns:
        int: User ID of the newly created user
        
    Raises:
        sqlite3.IntegrityError: If username already exists
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id
