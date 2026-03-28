"""
Authentication utilities for PhysioAI.

Handles password hashing and session-based authentication.
"""

from functools import wraps
from flask import session, jsonify
from backend.db_mongo import users_collection

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """
    Hash a password using werkzeug's secure hashing.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password (never store raw passwords)
    """
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password_hash: Stored password hash
        password: Plain text password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)


def login_required(f):
    """
    Decorator to require authentication for a route.
    
    Checks if user_id is in Flask session.
    Returns HTTP 401 if not authenticated.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            user_id = session['user_id']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function
