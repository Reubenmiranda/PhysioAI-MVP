# PhysioAI MVP

An AI-powered physiotherapy session assistant that uses real-time pose detection to guide users through exercises, count reps, and provide live posture feedback — all through a webcam.

---

## Features

- **Real-time pose detection** via MediaPipe running in the browser
- **Rep counting** with correct/incorrect classification based on joint angles
- **Live AI feedback** on posture during each exercise
- **Exercise catalog** — select 5 from 10 available exercises to build a session
- **Session summary** — overall score and per-exercise breakdown after each session
- **Session history** — view all past sessions with full exercise detail
- **User authentication** — register and login with secure password hashing
- **Cloud database** — all user data and sessions stored in Supabase

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, Tailwind CSS, Vanilla JavaScript |
| Pose Detection | MediaPipe Pose (browser, via CDN) |
| Backend | Python, Flask, Flask-CORS |
| Database | Supabase (PostgreSQL) |
| Design System | Stitch |

---

## Project Structure

```
PhysioAI-MVP/
├── frontend/               # Static frontend (HTML/CSS/JS)
│   ├── index.html          # Login page
│   ├── signup.html         # Registration page
│   ├── exercises.html      # Exercise selection
│   ├── session.html        # Live session with webcam
│   ├── summary.html        # Post-session summary
│   ├── history.html        # Session history list
│   ├── session-detail.html # Individual session detail
│   ├── css/
│   └── js/
├── backend/                # Flask API server
│   ├── app.py              # Main Flask app and routes
│   ├── auth.py             # Password hashing and auth helpers
│   └── db_supabase.py      # Supabase database layer
├── utils/                  # Core exercise logic
│   ├── exercise_logic.py   # Joint angle thresholds and rep detection
│   ├── pose_module.py      # MediaPipe pose detection wrapper
│   └── session_manager.py  # Session state and scoring
├── models/                 # MediaPipe model files
├── requirements.txt
└── .env                    # Environment variables (not committed)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A Supabase project with the required tables
- A webcam

### 1. Clone the repository

```bash
git clone https://github.com/Reubenmiranda/PhysioAI-MVP.git
cd PhysioAI-MVP
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
FLASK_SECRET_KEY=your_random_secret_key
```

### 4. Run the backend

```bash
python backend/app.py
```

Backend runs at `http://localhost:5000`

### 5. Run the frontend

```bash
cd frontend
python -m http.server 3000
```

Frontend runs at `http://localhost:3000`

---

## Exercises

The app includes 10 guided physiotherapy exercises:

1. Standing Hip Flexion
2. Glute Bridge
3. Cobra Pose
4. Standing March
5. Standing Forward Arm Raise
6. Standing Lateral Arm Raise
7. Shoulder Shrugs
8. Standing Trunk Side Bend
9. Standing Arm Circles
10. Neutral Posture Hold

Users select 5 exercises per session. Each exercise targets 10 correct reps and is scored 0–10. The overall session score is calculated as a percentage of correct reps across all exercises.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a new user |
| POST | `/login` | Login and create session |
| POST | `/logout` | Logout |
| GET | `/exercises` | Get available exercises |
| POST | `/session/start` | Start a new session |
| POST | `/session/update` | Send pose landmarks, get feedback |
| POST | `/session/next` | Move to next exercise |
| POST | `/session/end` | End session and save to database |
| GET | `/session/status` | Get current session status |
| GET | `/history` | Get all past sessions |
| GET | `/history/<session_id>` | Get full detail for a session |

---

## Disclaimer

PhysioAI is a prototype assistant tool and is **not a medical device**. It does not provide clinical diagnoses or medical advice. Always consult a qualified physiotherapist before starting any exercise program.
