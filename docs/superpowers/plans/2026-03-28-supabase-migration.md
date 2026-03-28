# Supabase Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace MongoDB with Supabase (PostgreSQL) as the persistence layer for PhysioAI's user and session data.

**Architecture:** A new `backend/db_supabase.py` replaces `backend/db_mongo.py` with identical function signatures so `app.py` changes are minimal. Flask cookie sessions remain the auth mechanism — no Supabase Auth. Supabase tables (`users`, `sessions`) are already created in the project.

**Tech Stack:** Python 3, Flask, supabase-py, pytest, unittest.mock

---

## File Map

| Action | File | Purpose |
|--------|------|---------|
| Create | `backend/db_supabase.py` | Supabase client + all DB functions |
| Create | `tests/__init__.py` | Makes tests a package |
| Create | `tests/test_db_supabase.py` | Unit tests for db_supabase.py |
| Modify | `backend/auth.py` | Remove dead `db_mongo` import |
| Modify | `backend/app.py` | Swap DB imports + fix `_id`, timestamps, error handling |
| Modify | `requirements.txt` | Remove pymongo, add supabase |
| Modify | `.env` | Swap MONGO_URI for SUPABASE_URL + SUPABASE_KEY |
| Delete | `backend/db_mongo.py` | Replaced by db_supabase.py |
| Delete | `backend/db.py` | Unused SQLite module |
| Delete | `backend/test_mongo_connection.py` | Obsolete test |

---

## Task 1: Update dependencies and environment

**Files:**
- Modify: `requirements.txt`
- Modify: `.env`

- [ ] **Step 1: Update requirements.txt**

Replace the entire file contents with:

```text
mediapipe>=0.10.0
opencv-python
numpy

# Flask Backend
Flask>=3.0.0
Flask-CORS>=4.0.0
python-dotenv>=1.0.0
werkzeug>=3.0.0

# Supabase Database
supabase>=2.0.0
```

- [ ] **Step 2: Install the new dependency**

Run from project root (activate venv first):
```bash
.venv\Scripts\activate
pip install supabase
```

Expected: supabase and its dependencies (postgrest, httpx, etc.) install successfully.

- [ ] **Step 3: Update .env**

Remove the line:
```
MONGO_URI=...
```

Add these two lines:
```
SUPABASE_URL=https://cfpdohvqnbaqvsfyrxsh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmcGRvaHZxbmJhcXZzZnlyeHNoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2NzU5NTMsImV4cCI6MjA5MDI1MTk1M30.WkPcYgdg52MKen3GIUQRIK6QMWm6ycCt_kNNf5KyS1A
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: swap pymongo for supabase dependency"
```

---

## Task 2: Fix auth.py (remove dead import)

**Files:**
- Modify: `backend/auth.py`

**Do this before deleting db_mongo.py — otherwise the app will fail to start.**

- [ ] **Step 1: Remove the dead import from auth.py**

In `backend/auth.py`, delete line 9:
```python
from backend.db_mongo import users_collection
```

`users_collection` is never used anywhere in `auth.py`. Safe to remove.

- [ ] **Step 2: Verify the module imports cleanly**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python -c "import sys; sys.path.insert(0, 'backend'); import auth; print('auth OK')"
```

Expected: `auth OK`

- [ ] **Step 3: Commit**

```bash
git add backend/auth.py
git commit -m "fix: remove unused db_mongo import from auth.py"
```

---

## Task 3: Create db_supabase.py (TDD)

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_db_supabase.py`
- Create: `backend/db_supabase.py`

- [ ] **Step 1: Create empty tests package**

Create `tests/__init__.py` as an empty file.

- [ ] **Step 2: Write failing tests — create tests/test_db_supabase.py**

```python
"""
Unit tests for db_supabase.py.
All Supabase client calls are mocked — no real network requests.
"""
import pytest
from unittest.mock import MagicMock, patch


def _make_client():
    """Return a MagicMock that mimics the supabase-py fluent builder."""
    return MagicMock()


# ---------------------------------------------------------------------------
# create_user
# ---------------------------------------------------------------------------

def test_create_user_returns_uuid_string():
    mock_client = _make_client()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "aaaa-bbbb-cccc"}
    ]
    with patch("db_supabase._client", mock_client):
        from db_supabase import create_user
        result = create_user("test@example.com", "Alice", 30, "female", "hash123")
    assert result == "aaaa-bbbb-cccc"


def test_create_user_lowercases_email():
    mock_client = _make_client()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "aaaa-bbbb-cccc"}
    ]
    with patch("db_supabase._client", mock_client):
        from db_supabase import create_user
        create_user("TEST@EXAMPLE.COM", "Alice", 30, "female", "hash123")
    call_args = mock_client.table.return_value.insert.call_args[0][0]
    assert call_args["email"] == "test@example.com"


# ---------------------------------------------------------------------------
# get_user_by_email
# ---------------------------------------------------------------------------

def test_get_user_by_email_found():
    mock_client = _make_client()
    user_data = {"id": "aaaa", "email": "alice@example.com", "name": "Alice"}
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = user_data
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_by_email
        result = get_user_by_email("alice@example.com")
    assert result == user_data


def test_get_user_by_email_not_found():
    mock_client = _make_client()
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = None
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_by_email
        result = get_user_by_email("nobody@example.com")
    assert result is None


# ---------------------------------------------------------------------------
# get_user_by_id
# ---------------------------------------------------------------------------

def test_get_user_by_id_found():
    mock_client = _make_client()
    user_data = {"id": "aaaa", "email": "alice@example.com"}
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = user_data
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_by_id
        result = get_user_by_id("aaaa")
    assert result == user_data


def test_get_user_by_id_not_found():
    mock_client = _make_client()
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = None
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_by_id
        result = get_user_by_id("doesnt-exist")
    assert result is None


# ---------------------------------------------------------------------------
# save_session
# ---------------------------------------------------------------------------

def test_save_session_returns_uuid_string():
    mock_client = _make_client()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "sess-uuid-123"}
    ]
    with patch("db_supabase._client", mock_client):
        from db_supabase import save_session
        result = save_session(
            user_id="user-uuid-456",
            session_score=85.0,
            exercises=[{"exercise_name": "Cobra Pose", "total_reps": 10}],
            totals={"total_reps": 10, "total_correct_reps": 8, "total_incorrect_reps": 2}
        )
    assert result == "sess-uuid-123"


def test_save_session_maps_totals_to_columns():
    mock_client = _make_client()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "sess-uuid-123"}
    ]
    with patch("db_supabase._client", mock_client):
        from db_supabase import save_session
        save_session(
            user_id="user-uuid-456",
            session_score=85.0,
            exercises=[],
            totals={"total_reps": 10, "total_correct_reps": 8, "total_incorrect_reps": 2}
        )
    inserted = mock_client.table.return_value.insert.call_args[0][0]
    assert inserted["total_reps"] == 10
    assert inserted["total_correct_reps"] == 8
    assert inserted["total_incorrect_reps"] == 2


# ---------------------------------------------------------------------------
# get_user_sessions
# ---------------------------------------------------------------------------

def test_get_user_sessions_returns_list():
    mock_client = _make_client()
    sessions = [
        {"id": "s1", "session_score": 80.0, "timestamp": "2026-03-28T10:00:00+00:00"},
        {"id": "s2", "session_score": 75.0, "timestamp": "2026-03-27T10:00:00+00:00"},
    ]
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .limit.return_value
        .execute.return_value.data) = sessions
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_sessions
        result = get_user_sessions("user-uuid-456")
    assert result == sessions


def test_get_user_sessions_returns_empty_list_on_error():
    mock_client = _make_client()
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .limit.return_value
        .execute.side_effect) = Exception("network error")
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_user_sessions
        result = get_user_sessions("user-uuid-456")
    assert result == []


# ---------------------------------------------------------------------------
# get_session_by_id
# ---------------------------------------------------------------------------

def test_get_session_by_id_found():
    mock_client = _make_client()
    session_data = {"id": "sess-1", "user_id": "user-1", "session_score": 90.0}
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = session_data
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_session_by_id
        result = get_session_by_id("sess-1", "user-1")
    assert result == session_data


def test_get_session_by_id_not_found():
    mock_client = _make_client()
    (mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value.data) = None
    with patch("db_supabase._client", mock_client):
        from db_supabase import get_session_by_id
        result = get_session_by_id("bad-id", "user-1")
    assert result is None
```

- [ ] **Step 3: Run tests — verify they all FAIL**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python -m pytest tests/test_db_supabase.py -v --import-mode=importlib --pythonpath=backend
```

Expected: `ModuleNotFoundError: No module named 'db_supabase'`

- [ ] **Step 4: Create backend/db_supabase.py**

```python
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
```

- [ ] **Step 5: Run tests — verify all pass**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python -m pytest tests/test_db_supabase.py -v --import-mode=importlib --pythonpath=backend
```

Expected: 12 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/db_supabase.py tests/__init__.py tests/test_db_supabase.py
git commit -m "feat: add db_supabase.py with full test coverage"
```

---

## Task 4: Update app.py

**Files:**
- Modify: `backend/app.py`

- [ ] **Step 1: Swap the DB import block (~lines 50-59)**

Replace:
```python
from db_mongo import (
    create_user as create_user_mongo,
    get_user_by_email,
    get_user_by_id,
    save_session,
    get_user_sessions,
    get_session_by_id
)
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
```

With:
```python
import uuid
from postgrest.exceptions import APIError as PostgrestAPIError
from db_supabase import (
    create_user as create_user_mongo,
    get_user_by_email,
    get_user_by_id,
    save_session,
    get_user_sessions,
    get_session_by_id
)
```

- [ ] **Step 2: Fix duplicate email detection in `register` route**

Replace:
```python
    try:
        password_hash = hash_password(password)
        user_id = create_user_mongo(email, name, age, gender, password_hash)
        return jsonify({
            "message": "User registered successfully",
            "user_id": str(user_id)
        }), 201
    except DuplicateKeyError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": "Registration failed. Please try again."}), 500
```

With:
```python
    try:
        password_hash = hash_password(password)
        user_id = create_user_mongo(email, name, age, gender, password_hash)
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201
    except PostgrestAPIError as e:
        if e.code == "23505":
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Registration failed. Please try again."}), 500
    except Exception:
        return jsonify({"error": "Registration failed. Please try again."}), 500
```

- [ ] **Step 3: Fix `_id` in `login` route (two occurrences)**

Replace:
```python
    session['user_id'] = str(user['_id'])
    session['email'] = email
    session['name'] = user.get('name', '')

    return jsonify({
        "message": "Login successful",
        "user_id": str(user['_id']),
```

With:
```python
    session['user_id'] = user['id']
    session['email'] = email
    session['name'] = user.get('name', '')

    return jsonify({
        "message": "Login successful",
        "user_id": user['id'],
```

- [ ] **Step 4: Fix `_id` and timestamp in `/history` route**

Replace:
```python
        for sess in sessions:
            sessions_list.append({
                "session_id": str(sess['_id']),
                "timestamp": sess['timestamp'].isoformat(),
                "session_score": sess['session_score']
            })
```

With:
```python
        for sess in sessions:
            sessions_list.append({
                "session_id": sess['id'],
                "timestamp": sess['timestamp'],
                "session_score": sess['session_score']
            })
```

- [ ] **Step 5: Fix UUID validation in `/history/<session_id>` route**

Replace:
```python
    if not ObjectId.is_valid(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400
```

With:
```python
    try:
        uuid.UUID(session_id)
    except ValueError:
        return jsonify({"error": "Invalid session ID format"}), 400
```

- [ ] **Step 6: Fix `_id` and timestamp in `/history/<session_id>` response**

Replace:
```python
        response = {
            "session_id": str(session_doc['_id']),
            "timestamp": session_doc['timestamp'].isoformat(),
            "session_score": session_doc['session_score'],
            "exercises": session_doc['exercises']
        }
```

With:
```python
        response = {
            "session_id": session_doc['id'],
            "timestamp": session_doc['timestamp'],
            "session_score": session_doc['session_score'],
            "exercises": session_doc['exercises']
        }
```

- [ ] **Step 7: Smoke test — verify server starts**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python backend/app.py
```

Expected: `* Running on http://0.0.0.0:5000` with no import errors. Stop with Ctrl+C.

- [ ] **Step 8: Commit**

```bash
git add backend/app.py
git commit -m "feat: migrate app.py from MongoDB to Supabase"
```

---

## Task 5: Delete old files

**Files:**
- Delete: `backend/db_mongo.py`
- Delete: `backend/db.py`
- Delete: `backend/test_mongo_connection.py`

- [ ] **Step 1: Delete the three obsolete files**

```bash
rm "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code\backend\db_mongo.py"
rm "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code\backend\db.py"
rm "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code\backend\test_mongo_connection.py"
```

- [ ] **Step 2: Verify the app still starts**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python backend/app.py
```

Expected: clean start, no errors. Stop with Ctrl+C.

- [ ] **Step 3: Run full test suite**

```bash
.venv\Scripts\python -m pytest tests/test_db_supabase.py -v --import-mode=importlib --pythonpath=backend
```

Expected: all 12 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove obsolete MongoDB files"
```

---

## Task 6: End-to-end verification

- [ ] **Step 1: Start the backend**

```bash
cd "C:\Users\REUBEN\OneDrive\Desktop\Major Project- Claude Code"
.venv\Scripts\python backend/app.py
```

- [ ] **Step 2: Register a test user**

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"name\":\"Test User\",\"age\":25,\"gender\":\"male\",\"password\":\"test123\"}"
```

Expected: HTTP 201 with `{"message": "User registered successfully", "user_id": "<uuid>"}`

- [ ] **Step 3: Login**

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
```

Expected: HTTP 200 with `{"message": "Login successful", "user_id": "<uuid>", ...}`

- [ ] **Step 4: Verify user appears in Supabase dashboard**

Open https://supabase.com/dashboard/project/cfpdohvqnbaqvsfyrxsh → Table Editor → users. The test user should be visible.

- [ ] **Step 5: Test duplicate registration returns 409**

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"name\":\"Test User\",\"age\":25,\"gender\":\"male\",\"password\":\"test123\"}"
```

Expected: HTTP 409 with `{"error": "Email already registered"}`

- [ ] **Step 6: Clean up test data**

In the Supabase SQL Editor run:
```sql
DELETE FROM users WHERE email = 'test@example.com';
```

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: complete MongoDB to Supabase migration"
```
