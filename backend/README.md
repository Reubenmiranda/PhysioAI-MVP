# PhysioAI Backend

Flask backend server for PhysioAI Phase B (MongoDB Database Integration).

## Setup

1. **Install dependencies** (from project root):
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and start MongoDB locally**:
   ```bash
   # Windows (using MongoDB Community Edition)
   # Download from: https://www.mongodb.com/try/download/community
   # MongoDB should run on mongodb://localhost:27017
   
   # Verify MongoDB is running:
   mongosh
   # or
   mongo
   ```

3. **Configure environment variables**:
   - Ensure `.env` file exists at project root with:
     ```
     FLASK_SECRET_KEY=your_secret_key_here
     MONGO_URI=mongodb://localhost:27017
     ```

4. **Run Flask development server**:
   ```bash
   python backend/app.py
   ```
   
   Or from the backend directory:
   ```bash
   cd backend
   python app.py
   ```

## Endpoints (Phase B)

### Health Check
- **GET** `/ping`
  - Returns: `{"status": "ok"}`
  - Purpose: Verify backend is running

### Root
- **GET** `/`
  - Returns: API information and available endpoints
  - Purpose: Basic API info

### Authentication
- **POST** `/register`
  - Body: `{"email": "user@example.com", "name": "Full Name", "age": 25, "gender": "male", "password": "password"}`
  - Returns: `201 Created` with user_id
  - Purpose: Register new user (persisted in MongoDB)

- **POST** `/login`
  - Body: `{"email": "user@example.com", "password": "password"}`
  - Returns: `200 OK` with session cookie
  - Purpose: Login and create session (validates against MongoDB)
  - Note: Does NOT auto-register - user must exist

- **POST** `/logout`
  - Returns: `200 OK`
  - Purpose: Logout and clear session

### Exercises
- **GET** `/exercises` (requires login)
  - Returns: List of available exercises with descriptions
  - Purpose: Get exercise catalog for session selection

### Session Management
- **POST** `/session/start` (requires login)
  - Body: `{"exercises": ["Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4", "Exercise 5"]}`
  - Returns: `200 OK` with current exercise
  - Purpose: Start new session with 5 selected exercises

- **POST** `/session/update` (requires login)
  - Body: `{"landmarks": {...}, "visibility": {...}}`
  - Returns: Real-time feedback and metrics
  - Purpose: Update current exercise with pose landmarks

- **POST** `/session/next` (requires login)
  - Returns: Next exercise name or session completion
  - Purpose: Manually move to next exercise

- **POST** `/session/end` (requires login)
  - Returns: Final session score and exercise metrics
  - Purpose: End session and save to MongoDB
  - Note: Session data is persisted and survives server restarts

- **GET** `/session/status` (requires login)
  - Returns: Current session status
  - Purpose: Check if user has active session

### History
- **GET** `/history` (requires login)
  - Returns: List of user's completed sessions (newest first)
  - Purpose: Retrieve session history from MongoDB
  - Format: `[{"session_id": "...", "timestamp": "...", "session_score": 87.5}, ...]`

- **GET** `/history/<session_id>` (requires login)
  - Returns: Detailed session data including exercise breakdown
  - Purpose: View specific session details
  - Security: Validates session belongs to requesting user

## Project Structure

```
PhysioAI/
├── backend/
│   ├── __init__.py      # Backend package marker
│   ├── app.py           # Flask entry point (Phase B integrated)
│   ├── auth.py          # Authentication utilities (login_required decorator)
│   ├── db_mongo.py      # MongoDB connection and utilities (Phase B)
│   └── README.md        # This file
├── utils/               # Core PhysioAI logic (DO NOT MODIFY)
│   ├── pose_module.py
│   ├── exercise_logic.py
│   └── session_manager.py
├── .env                 # Environment variables (not in git)
├── requirements.txt     # Python dependencies (includes pymongo)
└── main.py             # Console prototype (still works)
```

## Import Path Handling

The `backend/app.py` automatically adds the project root to `sys.path`, so imports from `utils/` work correctly:

```python
from utils.pose_module import PoseDetector
from utils.session_manager import SessionManager
from utils.exercise_logic import default_exercise_configs
```

## MongoDB Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "name": "Full Name",
  "age": 25,
  "gender": "male",
  "password_hash": "hashed_password",
  "created_at": ISODate("2026-02-02T...")
}
```
- Index: `email` (unique)

### Sessions Collection
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "timestamp": ISODate("2026-02-02T..."),
  "session_score": 87.5,
  "exercises": [
    {
      "exercise_name": "Standing Hip Flexion",
      "total_reps": 12,
      "correct_reps": 10,
      "incorrect_reps": 2,
      "posture_correctness_ratio": 0.85
    }
  ]
}
```

## Testing MongoDB Integration

1. **Start MongoDB** (must be running on `localhost:27017`)

2. **Test registration**:
   ```bash
   curl -X POST http://localhost:5000/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","name":"Test User","age":25,"gender":"male","password":"password123"}'
   ```

3. **Verify in MongoDB**:
   ```bash
   mongosh
   use physioai
   db.users.find()
   ```

4. **Test login**:
   ```bash
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"password123"}' \
     -c cookies.txt
   ```

5. **Complete a session and verify persistence**:
   - Start session → Update with landmarks → End session
   - Restart Flask server
   - Check `/history` - data should persist

6. **Verify sessions in MongoDB**:
   ```bash
   mongosh
   use physioai
   db.sessions.find()
   ```

## Notes

- **Core logic remains locked**: `utils/pose_module.py`, `utils/exercise_logic.py`, and `utils/session_manager.py` are NOT modified
- **MongoDB is local only**: For demo purposes, using `mongodb://localhost:27017`
- **No cloud MongoDB**: Keeps deployment simple
- **Sessions persist**: Data survives server restarts and browser closes
- **Healthcare-safe**: Non-diagnostic language throughout
- **Security**: User validation, password hashing, cross-user access prevention

## Next Steps (Phase C+)

- Frontend integration with history display
- OpenAI report generation
- Advanced analytics and visualizations
- Export session data (PDF/CSV)
