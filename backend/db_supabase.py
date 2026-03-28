"""
Supabase database utilities for PhysioAI.

Replaces db_mongo.py. Exposes identical function signatures so app.py
requires minimal changes.

Tables (already created in Supabase):
  users    — id, email, name, age, gender, password_hash, created_at
  sessions — id, user_id, timestamp, session_score, exercises (JSONB),
             total_reps, total_correct_reps, total_incorrect_reps
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _client = create_client(url, key)
    return _client


# ============================================================================
# User Management
# ============================================================================

def create_user(email: str, name: str, age: int, gender: str, password_hash: str) -> str:
    """
    Insert a new user. Returns UUID string of the created row.
    Raises postgrest.exceptions.APIError with code '23505' on duplicate email.
    """
    client = _get_client()
    response = client.table("users").insert({
        "email": email.lower().strip(),
        "name": name.strip(),
        "age": age,
        "gender": gender,
        "password_hash": password_hash,
    }).execute()
    return response.data[0]["id"]


def get_user_by_email(email: str) -> Optional[Dict]:
    """Return user dict for email, or None if not found."""
    client = _get_client()
    response = (
        client.table("users")
        .select("*")
        .eq("email", email.lower().strip())
        .maybe_single()
        .execute()
    )
    return response.data


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Return user dict for UUID, or None if not found."""
    client = _get_client()
    response = (
        client.table("users")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return response.data


# ============================================================================
# Session Management
# ============================================================================

def save_session(
    user_id: str,
    session_score: float,
    exercises: list,
    totals: Optional[Dict] = None
) -> str:
    """
    Save a completed session. Returns UUID string of the created row.
    totals keys: total_reps, total_correct_reps, total_incorrect_reps.
    """
    client = _get_client()
    row = {
        "user_id": user_id,
        "session_score": session_score,
        "exercises": exercises,
    }
    if totals:
        row["total_reps"] = totals.get("total_reps")
        row["total_correct_reps"] = totals.get("total_correct_reps")
        row["total_incorrect_reps"] = totals.get("total_incorrect_reps")
    response = client.table("sessions").insert(row).execute()
    return response.data[0]["id"]


def get_user_sessions(user_id: str, limit: int = 50) -> list:
    """
    Return summary list (id, session_score, timestamp) for a user's sessions,
    newest first. Returns [] on error.
    """
    client = _get_client()
    try:
        response = (
            client.table("sessions")
            .select("id, session_score, timestamp")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception:
        return []


def get_session_by_id(session_id: str, user_id: str) -> Optional[Dict]:
    """
    Return full session dict for (session_id, user_id), or None.
    The user_id check prevents cross-user access.
    """
    client = _get_client()
    response = (
        client.table("sessions")
        .select("*")
        .eq("id", session_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return response.data
