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
