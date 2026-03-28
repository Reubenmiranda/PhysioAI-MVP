"""
PhysioAI Flask Backend Entry Point

This is the Flask web server for Phase B (MongoDB Database Integration).
Core exercise logic, pose detection, and session management remain in utils/.

Phase B Features:
- MongoDB user persistence (email, name, age, gender)
- User authentication (register/login) with MongoDB
- Exercise listing API
- Session lifecycle management (start/update/next/end)
- Session persistence in MongoDB
- Session history retrieval (list and detail views)
"""

import os
import sys
from pathlib import Path
from typing import Dict

# Add project root to Python path so we can import from utils/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add backend directory to path for backend utilities
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file at project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Import core PhysioAI modules
try:
    from utils.pose_module import PoseDetector
    from utils.session_manager import SessionManager
    from utils.exercise_logic import default_exercise_configs
except ImportError as e:
    print(f"Error importing utils modules: {e}")
    print(f"Project root: {project_root}")
    sys.exit(1)

# Import backend utilities
from auth import hash_password, verify_password, login_required
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

# Initialize Flask app
app = Flask(__name__)

# Load Flask secret key from environment
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Enable CORS for local development only
CORS(app, supports_credentials=True)  # Allow credentials for session cookies

# In-memory storage for active sessions
# Format: {user_id (str): SessionManager instance}
active_sessions: Dict[str, SessionManager] = {}

# Valid joint names (shoulder + hip only)
VALID_JOINTS = {"LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP"}

# Exercise descriptions for API (non-diagnostic, safe descriptions)
EXERCISE_DESCRIPTIONS = {
    "Standing Hip Flexion": "Gently lift one knee forward while maintaining balance. This exercise promotes hip mobility.",
    "Glute Bridge": "Lie on your back and lift your hips toward the ceiling. Keep movements slow and controlled.",
    "Cobra Pose": "Lie face down and gently lift your chest using your arms. Keep the motion small and comfortable.",
    "Standing March": "Alternate lifting each knee slightly while standing. Focus on controlled, steady movements.",
    "Standing Forward Arm Raise": "Slowly raise both arms forward to shoulder height. Keep movements smooth and controlled.",
    "Standing Lateral Arm Raise": "Gently raise both arms out to your sides to shoulder height. Move slowly and steadily.",
    "Shoulder Shrugs": "Lift your shoulders toward your ears and lower them slowly. Keep movements controlled and relaxed.",
    "Standing Trunk Side Bend": "Gently lean your torso to one side while keeping your hips stable. Use small, controlled movements.",
    "Standing Arm Circles": "Make small circular motions with your arms. Keep the movement smooth and comfortable.",
    "Neutral Posture Hold": "Stand tall with shoulders aligned over hips. Hold this position with good alignment."
}


@app.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - basic info about the API."""
    return jsonify({
        "name": "PhysioAI Backend",
        "version": "2.2.0",
        "status": "Phase C - Supabase Database Integration",
        "endpoints": {
            "health": "/ping",
            "auth": ["/register", "/login", "/logout"],
            "exercises": "/exercises",
            "sessions": ["/session/start", "/session/update", "/session/next", "/session/end", "/session/status"],
            "history": ["/history", "/history/<session_id>"]
        }
    }), 200


# ============================================================================
# PART 1: Authentication Routes
# ============================================================================

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Input JSON:
        {
            "email": "string",
            "name": "string",
            "age": number,
            "gender": "string",
            "password": "string"
        }
    
    Returns:
        Success: 201 with {"message": "User registered successfully"}
        Error: 400/409 with {"error": "message"}
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    email = data.get('email')
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    password = data.get('password')
    
    # Check required fields
    if not all([email, name, age, gender, password]):
        return jsonify({"error": "All fields are required: email, name, age, gender, password"}), 400
    
    # Validate email format (basic)
    if '@' not in email or '.' not in email:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate name
    if len(name.strip()) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    
    # Validate age
    try:
        age = int(age)
        if age < 13 or age > 120:
            return jsonify({"error": "Age must be between 13 and 120"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Age must be a valid number"}), 400
    
    # Validate gender
    valid_genders = ["male", "female", "other", "prefer not to say"]
    if gender.lower() not in valid_genders:
        return jsonify({"error": "Invalid gender value"}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Create user in MongoDB
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


@app.route('/login', methods=['POST'])
def login():
    """
    Login user and create session.
    Does NOT auto-register - user must exist in MongoDB.
    
    Input JSON:
        {
            "email": "string",
            "password": "string"
        }
    
    Returns:
        Success: 200 with {"message": "Login successful", "user_id": str}
        Error: 401 with {"error": "message"}
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Get user from MongoDB
    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Verify password
    if not verify_password(user['password_hash'], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Create Flask session
    session['user_id'] = user['id']
    session['email'] = email
    session['name'] = user.get('name', '')

    return jsonify({
        "message": "Login successful",
        "user_id": user['id'],
        "email": email,
        "name": user.get('name', '')
    }), 200


@app.route('/logout', methods=['POST'])
def logout():
    """Logout user and clear session."""
    user_id = session.get('user_id')
    
    # Clear active session if exists
    if user_id and user_id in active_sessions:
        del active_sessions[user_id]
    
    session.clear()
    return jsonify({"message": "Logout successful"}), 200


# ============================================================================
# PART 2: Exercises API
# ============================================================================

@app.route('/exercises', methods=['GET'])
@login_required
def get_exercises():
    """
    Get list of available exercises.
    
    Returns:
        200 with {
            "exercises": [
                {
                    "name": "Exercise Name",
                    "description": "Safe, non-diagnostic description"
                },
                ...
            ]
        }
    """
    exercise_configs = default_exercise_configs()
    
    exercises = []
    for name in exercise_configs.keys():
        exercises.append({
            "name": name,
            "description": EXERCISE_DESCRIPTIONS.get(name, "A controlled movement exercise. Follow instructions carefully.")
        })
    
    return jsonify({"exercises": exercises}), 200


# ============================================================================
# PART 3: Session Flow APIs
# ============================================================================

@app.route('/session/start', methods=['POST'])
@login_required
def start_session():
    """
    Start a new physiotherapy session.
    
    Input JSON:
        {
            "exercises": ["Exercise Name 1", "Exercise Name 2", ...]  # Exactly 5
        }
    
    Returns:
        Success: 200 with {"message": "Session started", "current_exercise": "..."}
        Error: 400 with {"error": "message"}
    """
    user_id = session.get('user_id')
    
    # Check if user already has an active session
    if user_id in active_sessions:
        return jsonify({"error": "You already have an active session. End it before starting a new one."}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    exercises = data.get('exercises')
    if not exercises:
        return jsonify({"error": "Exercises list is required"}), 400
    
    # Enforce exactly 5 exercises
    if len(exercises) != 5:
        return jsonify({"error": "Exactly 5 exercises must be selected for a session"}), 400
    
    # Validate exercise names exist
    exercise_configs = default_exercise_configs()
    invalid_exercises = [ex for ex in exercises if ex not in exercise_configs]
    if invalid_exercises:
        return jsonify({
            "error": f"Invalid exercise names: {', '.join(invalid_exercises)}"
        }), 400
    
    # Initialize SessionManager
    try:
        session_manager = SessionManager()
        session_manager.configure_session(exercises)
        active_sessions[user_id] = session_manager
        
        current_exercise = session_manager.get_current_exercise_name()
        return jsonify({
            "message": "Session started successfully",
            "current_exercise": current_exercise,
            "total_exercises": 5
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to start session: {str(e)}"}), 500


@app.route('/session/update', methods=['POST'])
@login_required
def update_session():
    """
    Update current exercise with pose landmarks.
    
    Input JSON:
        {
            "landmarks": {
                "LEFT_SHOULDER": [x, y],
                "RIGHT_SHOULDER": [x, y],
                "LEFT_HIP": [x, y],
                "RIGHT_HIP": [x, y]
            },
            "visibility": {  # Optional but recommended
                "LEFT_SHOULDER": 0.98,
                ...
            }
        }
    
    Returns:
        Success: 200 with {
            "feedback": "string",
            "current_exercise": "string",
            "metrics": {
                "total_reps": int,
                "correct_reps": int,
                "score": int (0-10)
            },
            "session_active": bool
        }
    """
    user_id = session.get('user_id')
    
    # Check if user has active session
    if user_id not in active_sessions:
        return jsonify({"error": "No active session. Start a session first."}), 400
    
    session_manager = active_sessions[user_id]
    
    if not session_manager.session_active:
        return jsonify({"error": "Session is not active"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    landmarks = data.get('landmarks')
    visibility = data.get('visibility', {})
    
    # Validate landmarks
    if not landmarks:
        return jsonify({"error": "Landmarks are required"}), 400
    
    # Validate required joints exist
    missing_joints = VALID_JOINTS - set(landmarks.keys())
    if missing_joints:
        return jsonify({
            "error": f"Missing required joints: {', '.join(missing_joints)}"
        }), 400
    
    # Validate visibility (if provided)
    if visibility:
        for joint_name, vis in visibility.items():
            if joint_name in VALID_JOINTS and vis < 0.5:
                return jsonify({
                    "error": f"Joint {joint_name} visibility ({vis}) is below threshold (0.5). Ensure good lighting and camera position."
                }), 400
    
    # Convert landmarks format: [x, y] -> (x, y) tuple
    landmarks_dict = {k: tuple(v) if isinstance(v, list) else v for k, v in landmarks.items()}
    
    # Update session with landmarks
    try:
        feedback = session_manager.update_with_landmarks(landmarks_dict)
        current_exercise = session_manager.get_current_exercise_name()
        
        # Get current exercise metrics
        metrics = session_manager.metrics.exercises.get(current_exercise)
        metrics_data = {}
        if metrics:
            metrics_data = {
                "total_reps": metrics.total_reps,
                "correct_reps": metrics.correct_reps,
                "incorrect_reps": metrics.incorrect_reps,
                "score": min(metrics.correct_reps, 10)  # Capped at 10
            }
        
        return jsonify({
            "feedback": feedback,
            "current_exercise": current_exercise,
            "metrics": metrics_data,
            "session_active": session_manager.session_active
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update session: {str(e)}"}), 500


@app.route('/session/next', methods=['POST'])
@login_required
def next_exercise():
    """
    Move to the next exercise in the session.
    
    Returns:
        Success: 200 with {
            "message": "Moved to next exercise",
            "current_exercise": "string",
            "session_active": bool
        }
    """
    user_id = session.get('user_id')
    
    # Check if user has active session
    if user_id not in active_sessions:
        return jsonify({"error": "No active session. Start a session first."}), 400
    
    session_manager = active_sessions[user_id]
    
    if not session_manager.session_active:
        return jsonify({"error": "Session is not active"}), 400
    
    # Move to next exercise
    session_manager.next_exercise()
    
    current_exercise = session_manager.get_current_exercise_name()
    
    return jsonify({
        "message": "Moved to next exercise" if current_exercise else "Session completed",
        "current_exercise": current_exercise,
        "session_active": session_manager.session_active
    }), 200


@app.route('/session/end', methods=['POST'])
@login_required
def end_session():
    """
    End the current session, save to MongoDB, and return final metrics.
    
    Returns:
        Success: 200 with {
            "message": "Session ended",
            "session_id": str,
            "session_score": float (0-100),
            "exercises": [
                {
                    "exercise_name": str,
                    "total_reps": int,
                    "correct_reps": int,
                    "incorrect_reps": int,
                    "posture_correctness_ratio": float (0-1)
                },
                ...
            ]
        }
    """
    user_id = session.get('user_id')
    
    # Check if user has active session
    if user_id not in active_sessions:
        return jsonify({"error": "No active session. Start a session first."}), 400
    
    session_manager = active_sessions[user_id]
    
    # End session and compute score
    session_manager.end_session()
    
    # Prepare exercises list for MongoDB (clean format)
    exercises_list = []
    for exercise_name, metrics in session_manager.metrics.exercises.items():
        exercises_list.append({
            "exercise_name": exercise_name,
            "total_reps": metrics.total_reps,
            "correct_reps": metrics.correct_reps,
            "incorrect_reps": metrics.incorrect_reps,
            "posture_correctness_ratio": round(metrics.posture_correctness_ratio, 4)
        })
    
    # Aggregate totals across exercises
    total_correct_reps = sum(ex["correct_reps"] for ex in exercises_list)
    total_reps = sum(ex["total_reps"] for ex in exercises_list)
    total_incorrect_reps = max(total_reps - total_correct_reps, 0)
    overall_score = round(session_manager.metrics.session_score, 2)

    # Save session to MongoDB
    try:
        session_id = save_session(
            user_id=user_id,
            session_score=overall_score,
            exercises=exercises_list,
            totals={
                "total_correct_reps": total_correct_reps,
                "total_incorrect_reps": total_incorrect_reps,
                "total_reps": total_reps,
            },
        )
    except Exception as e:
        # Log error but still return metrics to user
        print(f"[Error] Failed to save session to MongoDB: {e}")
        session_id = None
    
    # Clear active session from memory
    del active_sessions[user_id]
    
    # Return response in frontend-compatible format
    response_body = {
        "message": "Session ended successfully",
        "session_id": str(session_id) if session_id else None,
        "overall_score": overall_score,
        "total_correct_reps": total_correct_reps,
        "total_incorrect_reps": total_incorrect_reps,
        "total_reps": total_reps,
        "exercise_breakdown": exercises_list,
        # Backwards compatibility fields
        "session_score": overall_score,
        "exercises": exercises_list,
    }

    return jsonify(response_body), 200


@app.route('/session/status', methods=['GET'])
@login_required
def session_status():
    """
    Get current session status.
    
    Returns:
        Success: 200 with {
            "has_active_session": bool,
            "current_exercise": "string" or null,
            "session_active": bool
        }
    """
    user_id = session.get('user_id')
    
    has_session = user_id in active_sessions
    
    if not has_session:
        return jsonify({
            "has_active_session": False,
            "current_exercise": None,
            "session_active": False
        }), 200
    
    session_manager = active_sessions[user_id]
    current_exercise = session_manager.get_current_exercise_name()
    
    return jsonify({
        "has_active_session": True,
        "current_exercise": current_exercise,
        "session_active": session_manager.session_active
    }), 200


# ============================================================================
# PART 4: Session History APIs
# ============================================================================

@app.route('/history', methods=['GET'])
@login_required
def get_history():
    """
    Get list of all completed sessions for the logged-in user.
    
    Returns:
        Success: 200 with {
            "sessions": [
                {
                    "session_id": str,
                    "timestamp": str (ISO format),
                    "session_score": float
                },
                ...
            ]
        }
        
    Sessions are sorted by newest first.
    """
    user_id = session.get('user_id')
    
    try:
        sessions = get_user_sessions(user_id)
        
        # Format sessions for response
        sessions_list = []
        for sess in sessions:
            sessions_list.append({
                "session_id": sess['id'],
                "timestamp": sess['timestamp'],
                "session_score": sess['session_score']
            })
        
        return jsonify({"sessions": sessions_list}), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve session history"}), 500


@app.route('/history/<session_id>', methods=['GET'])
@login_required
def get_session_detail(session_id):
    """
    Get detailed information for a specific session.
    Validates that the session belongs to the requesting user.
    
    Args:
        session_id: MongoDB ObjectId of the session
        
    Returns:
        Success: 200 with {
            "session_id": str,
            "timestamp": str (ISO format),
            "session_score": float,
            "exercises": [
                {
                    "exercise_name": str,
                    "total_reps": int,
                    "correct_reps": int,
                    "incorrect_reps": int,
                    "posture_correctness_ratio": float
                },
                ...
            ]
        }
        Error: 400/404 with {"error": "message"}
    """
    user_id = session.get('user_id')
    
    # Validate session_id format
    try:
        uuid.UUID(session_id)
    except ValueError:
        return jsonify({"error": "Invalid session ID format"}), 400
    
    # Get session from MongoDB
    try:
        session_doc = get_session_by_id(session_id, user_id)
        
        if not session_doc:
            return jsonify({"error": "Session not found or access denied"}), 404
        
        # Format response
        response = {
            "session_id": session_doc['id'],
            "timestamp": session_doc['timestamp'],
            "session_score": session_doc['session_score'],
            "exercises": session_doc['exercises']
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve session details"}), 500


if __name__ == '__main__':
    # Run Flask development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
