"""
MongoDB database utilities for PhysioAI.

Manages connection to MongoDB and provides access to collections.

Collections:
- users: User accounts with authentication data
  Schema: {
    _id: ObjectId,
    email: string (unique),
    name: string,
    age: number,
    gender: string,
    password_hash: string,
    created_at: ISODate
  }

- sessions: Completed physiotherapy sessions
  Schema: {
    _id: ObjectId,
    user_id: ObjectId,
    timestamp: ISODate,
    session_score: number (0-100),
    exercises: [
      {
        exercise_name: string,
        total_reps: number,
        correct_reps: number,
        incorrect_reps: number,
        posture_correctness_ratio: number (0-1)
      }
    ]
  }
"""

from typing import Optional, Dict
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# MongoDB connection URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Initialize MongoDB client (connection is lazy, established on first operation)
client: Optional[MongoClient] = None
db = None
users_collection = None
sessions_collection = None


def get_db():
    """
    Get MongoDB database instance.
    Creates connection on first call and reuses it.

    Returns:
        Database: MongoDB database instance

    Raises:
        ConnectionFailure: If MongoDB is not accessible
    """
    global client, db, users_collection, sessions_collection

    if client is None:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')

            db = client["physioai"]
            users_collection = db["users"]
            sessions_collection = db["sessions"]

            # Create unique index on email for users collection
            users_collection.create_index("email", unique=True)

            print(f"[MongoDB] Connected successfully to {MONGO_URI}")
        except ConnectionFailure as e:
            print(f"[MongoDB] Connection failed: {e}")
            raise

    return db


# Initialize database connection on module import
try:
    get_db()
except Exception as e:
    print(f"[MongoDB] Warning: Could not connect on startup: {e}")
    print("[MongoDB] Will retry on first operation")


# ============================================================================
# User Management Functions
# ============================================================================


def create_user(email: str, name: str, age: int, gender: str, password_hash: str) -> ObjectId:
    """
    Create a new user in MongoDB.

    Args:
        email: User email (must be unique)
        name: User full name
        age: User age
        gender: User gender
        password_hash: Hashed password (never store raw passwords)

    Returns:
        ObjectId: MongoDB _id of the created user

    Raises:
        DuplicateKeyError: If email already exists
    """
    user_doc = {
        "email": email.lower().strip(),
        "name": name.strip(),
        "age": age,
        "gender": gender,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }

    result = users_collection.insert_one(user_doc)
    return result.inserted_id


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Retrieve a user by email.

    Args:
        email: User email to search for

    Returns:
        dict with user data if found, None otherwise
    """
    return users_collection.find_one({"email": email.lower().strip()})


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Retrieve a user by MongoDB ObjectId.

    Args:
        user_id: String representation of MongoDB ObjectId

    Returns:
        dict with user data if found, None otherwise
    """
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


# ============================================================================
# Session Management Functions
# ============================================================================

def save_session(
    user_id: str,
    session_score: float,
    exercises: list,
    totals: Optional[Dict[str, int]] = None
) -> ObjectId:
    """
    Save a completed physiotherapy session to MongoDB.

    Args:
        user_id: String representation of user's MongoDB ObjectId
        session_score: Overall session score (0-100)
        exercises: List of exercise dictionaries with metrics
        totals: Optional aggregated totals for the session

    Returns:
        ObjectId: MongoDB _id of the created session document
    """
    session_doc = {
        "user_id": ObjectId(user_id),
        "timestamp": datetime.utcnow(),
        "session_score": session_score,
        "exercises": exercises
    }

    if totals:
        session_doc.update(totals)

    result = sessions_collection.insert_one(session_doc)
    return result.inserted_id


def get_user_sessions(user_id: str, limit: int = 50) -> list:
    """
    Retrieve all sessions for a user, sorted by newest first.

    Args:
        user_id: String representation of user's MongoDB ObjectId
        limit: Maximum number of sessions to return (default 50)

    Returns:
        List of session documents with basic info
    """
    try:
        sessions = sessions_collection.find(
            {"user_id": ObjectId(user_id)},
            {"session_score": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(limit)

        return list(sessions)
    except Exception:
        return []


def get_session_by_id(session_id: str, user_id: str) -> Optional[Dict]:
    """
    Retrieve a specific session by ID.
    Validates that the session belongs to the requesting user.

    Args:
        session_id: String representation of session's MongoDB ObjectId
        user_id: String representation of user's MongoDB ObjectId

    Returns:
        dict with full session data if found and authorized, None otherwise
    """
    try:
        return sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": ObjectId(user_id)
        })
    except Exception:
        return None
