# PhysioAI: MongoDB → Supabase Migration Design

**Date:** 2026-03-28
**Scope:** Backend database layer only — Flask sessions, auth logic, and frontend are unchanged.

---

## Overview

Replace MongoDB (via `pymongo`) with Supabase (hosted PostgreSQL) as the persistence layer. The migration is a clean-slate swap — no existing data needs to be preserved. All function signatures in the new DB module mirror the old ones so `app.py` changes are minimal.

---

## Supabase Project

- **URL:** `https://cfpdohvqnbaqvsfyrxsh.supabase.co`
- **Auth strategy:** anon key used from the backend; RLS disabled (Flask sessions handle access control)

---

## Database Schema

Tables already created in Supabase via SQL Editor.

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, `gen_random_uuid()` |
| email | TEXT | UNIQUE NOT NULL |
| name | TEXT | NOT NULL |
| age | INTEGER | NOT NULL |
| gender | TEXT | NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### `sessions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, `gen_random_uuid()` |
| user_id | UUID | FK → users.id |
| timestamp | TIMESTAMPTZ | DEFAULT now() |
| session_score | FLOAT | NOT NULL |
| exercises | JSONB | Array of exercise dicts |
| total_reps | INTEGER | |
| total_correct_reps | INTEGER | |
| total_incorrect_reps | INTEGER | |

---

## Code Changes

### New file: `backend/db_supabase.py`

Initialises a `supabase-py` client using `SUPABASE_URL` and `SUPABASE_KEY` env vars. Exposes the same functions as `db_mongo.py`:

- **`create_user(email, name, age, gender, password_hash)`** → inserts into `users`, returns UUID string (`data[0]['id']`)
- **`get_user_by_email(email)`** → `.select("*").eq("email", email.lower().strip()).single()`, returns dict or None
- **`get_user_by_id(user_id)`** → `.select("*").eq("id", user_id).single()`, returns dict or None
- **`save_session(user_id, session_score, exercises, totals=None)`** → inserts into `sessions` with explicitly mapped columns:
  ```python
  row = {
      "user_id": user_id,
      "session_score": session_score,
      "exercises": exercises,
  }
  if totals:
      row["total_reps"] = totals.get("total_reps")
      row["total_correct_reps"] = totals.get("total_correct_reps")
      row["total_incorrect_reps"] = totals.get("total_incorrect_reps")
  ```
  Returns UUID string (`data[0]['id']`)
- **`get_user_sessions(user_id, limit=50)`** → `.select("id, session_score, timestamp").eq("user_id", user_id).order("timestamp", desc=True).limit(limit)`, returns list of dicts (summary fields only — avoids loading full `exercises` JSONB for the history list)
- **`get_session_by_id(session_id, user_id)`** → `.select("*").eq("id", session_id).eq("user_id", user_id).single()`, returns dict or None

**Timestamp handling:** Supabase returns timestamps as ISO 8601 strings, not Python `datetime` objects. All timestamp values are returned as-is (strings). `app.py` must not call `.isoformat()` on them — see `app.py` changes below.

### Modified: `backend/app.py`

1. **Import swap:** `from db_supabase import (create_user as create_user_mongo, get_user_by_email, get_user_by_id, save_session, get_user_sessions, get_session_by_id)`
2. **Remove pymongo/bson imports:** Delete `from pymongo.errors import DuplicateKeyError` and `from bson import ObjectId`
3. **Add uuid import:** `import uuid`
4. **Duplicate email detection** (in `register` route): Replace `except DuplicateKeyError` with:
   ```python
   from postgrest.exceptions import APIError
   except APIError as e:
       if e.code == "23505":  # PostgreSQL unique violation
           return jsonify({"error": "Email already registered"}), 409
       raise
   ```
5. **`_id` → `id` in `login` route** (two occurrences, lines ~230 and ~237):
   - `session['user_id'] = str(user['_id'])` → `session['user_id'] = user['id']`
   - `"user_id": str(user['_id'])` → `"user_id": user['id']`
6. **`/history` route** (line ~640): Replace:
   - `"session_id": str(sess['_id'])` → `"session_id": sess['id']`
   - `"timestamp": sess['timestamp'].isoformat()` → `"timestamp": sess['timestamp']` (already a string from Supabase)
7. **`/history/<session_id>` route** (lines ~692-698): Replace:
   - `"session_id": str(session_doc['_id'])` → `"session_id": session_doc['id']`
   - `"timestamp": session_doc['timestamp'].isoformat()` → `"timestamp": session_doc['timestamp']`
8. **UUID validation** (replacing `ObjectId.is_valid`):
   ```python
   try:
       uuid.UUID(session_id)
   except ValueError:
       return jsonify({"error": "Invalid session ID format"}), 400
   ```

### Modified: `backend/auth.py`

- Remove the unused import: `from backend.db_mongo import users_collection`
- **Note:** This import must be removed before or at the same time as `db_mongo.py` is deleted — if `db_mongo.py` is deleted first, the app will fail to start.

### Modified: `.env`

- Remove: `MONGO_URI`
- Add:
  ```
  SUPABASE_URL=https://cfpdohvqnbaqvsfyrxsh.supabase.co
  SUPABASE_KEY=<anon key>
  ```

### Modified: `requirements.txt`

- Remove: `pymongo` (this also removes `bson`, which is bundled with pymongo)
- Add: `supabase`

### Deleted files (in this order to avoid startup errors)

1. Fix `auth.py` first (remove the `db_mongo` import)
2. Then delete `backend/db_mongo.py`
3. Then delete `backend/db.py` (old unused SQLite module)
4. Then delete `backend/test_mongo_connection.py`

---

## Data Flow (unchanged)

```
Frontend JS → Flask route (app.py) → db_supabase.py → Supabase PostgreSQL
```

Flask session cookie still manages authentication state. No JWT tokens, no Supabase Auth.

---

## Out of Scope

- Frontend changes (covered in separate Stitch MCP frontend polish task)
- Supabase Auth / Row Level Security
- Data migration (clean slate)
