# PhysioAI
Smarter Rehab. Better Recovery.

---

## Summary
PhysioAI is a web app that guides users through physiotherapy exercises using their webcam. Users log in or register, select exactly 5 exercises, and perform them while MediaPipe Pose tracks their key joints in real time. The Flask backend scores reps and movement quality, and the UI shows live feedback during the session. After the session, the final summary page displays a metrics table, and the new Session History page lets users review past performance.

---

## Summary Page Changes (`summary.html` + `frontend/js/summary.js`)
- Shows ONLY the selected exercises for that session.
- Table shows one row per selected exercise with these metrics:
  - Exercise Name
  - Total Reps
  - Correct Reps
  - Incorrect Reps
  - Score (implemented as Posture Correctness %)
- When data is missing, defaults are shown:
  - Overall score displays `0.00 / 100`
  - Table cells use `0` values when rep/metrics fields are absent
- No red/green indicators are used; the table is numerical.

Data note:
- `session.js` stores the summary payload in `sessionStorage` under `physioai_session_summary`.
- `summary.js` builds the table using `exercise_breakdown` / `exercises` from that payload, and it computes the displayed score from the selected exercises’ rep counts (the payload also includes `session_score` / `overall_score` for reference).

---

## Session History (`history.html` + `frontend/js/history.js`)
### What `history.html` does
It displays completed sessions for the user in a card layout.

### How sessions are displayed
- Newest to oldest order (sorted by the session `date` descending).

### What data is shown per session
- Date/time
- Score (stored as `overall_score`)
- Exercises (a list of exercise names performed in that session)

### Where the data comes from (backend vs localStorage fallback)
- Backend persistence exists via Flask endpoints:
  - `GET /history` (list sessions)
  - `GET /history/<session_id>` (session detail)
- The current frontend `history.html` uses a localStorage fallback:
  - `session.js` appends completed sessions into `localStorage` key `physioai_session_history`
  - `history.js` reads and renders from that localStorage data

---

## Frontend Updates
- Branding:
  - `PhysioAI` appears top-left
  - the tagline appears directly below it
- History button is available on:
  - the exercises page (`exercises.html` → `history.html`)
  - the summary page (`summary.html` → `history.html`)

---

## Data Flow (Client → Flask → UI)
1. `session.js` live updates during the session
   - Sends `landmarks` (LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP) + optional `visibility`
   - POSTs to Flask at `/session/update`
2. Flask processes the landmarks
   - Validates required joints
   - Runs exercise logic + session manager to update rep/form metrics
   - Returns JSON containing `feedback`, `current_exercise`, and `metrics`
3. `session.js` ends the session
   - POSTs to `/session/end`
   - Receives back session metrics including:
     - `exercise_breakdown`
     - `exercises`
     - `session_score` (and `overall_score`)
   - Stores the payload in `sessionStorage` for the summary page
4. `summary.js` renders the final metrics table
   - Reads `exercise_breakdown`, `exercises`, and has access to `session_score` from `physioai_session_summary`
   - Uses the exercise breakdown to populate the per-exercise table and compute what’s displayed as the summary score

---

## Key Routes (Flask)
- Auth:
  - `POST /register`
  - `POST /login`
  - `POST /logout`
- Session:
  - `POST /session/start` (enforces exactly 5 selected exercises)
  - `POST /session/update` (joint coords → feedback + rep metrics)
  - `POST /session/end` (final metrics)
- History:
  - `GET /history`
  - `GET /history/<session_id>`

---

*Last updated: March 2026*

PhysioAI is a web app that guides users through physiotherapy exercises using their webcam. Users log in or register, select exactly 5 exercises, and perform them while MediaPipe Pose tracks their key joints in real time. The Flask backend scores reps and movement quality, and the UI shows live feedback during the session. After the session, the final summary page displays a metrics table, and the new Session History page lets users review past performance.

---

## Summary Page Changes (`summary.html` + `frontend/js/summary.js`)
- Shows ONLY the selected exercises for that session.
- Table shows one row per selected exercise with these metrics:
  - Exercise Name
  - Total Reps
  - Correct Reps
  - Incorrect Reps
  - Score (implemented as Posture Correctness %)
- When data is missing, defaults are shown:
  - Overall score displays `0.00 / 100`
  - Table cells use `0` values when rep/metrics fields are absent
- No red/green indicators are used; the table is numerical.

Data note:
- `session.js` stores the summary payload in `sessionStorage` under `physioai_session_summary`.
- `summary.js` builds the table using `exercise_breakdown` / `exercises` from that payload, and it computes the displayed score from the selected exercises’ rep counts (the payload also includes `session_score` / `overall_score` for reference).

---

## Session History (`history.html` + `frontend/js/history.js`)
### What `history.html` does
It displays completed sessions for the user in a card layout.

### How sessions are displayed
- Newest to oldest order (sorted by the session `date` descending).

### What data is shown per session
- Date/time
- Score (stored as `overall_score`)
- Exercises (a list of exercise names performed in that session)

### Where the data comes from (backend vs localStorage fallback)
- Backend persistence exists via Flask endpoints:
  - `GET /history` (list sessions)
  - `GET /history/<session_id>` (session detail)
- The current frontend `history.html` uses a localStorage fallback:
  - `session.js` appends completed sessions into `localStorage` key `physioai_session_history`
  - `history.js` reads and renders from that localStorage data

---

## Frontend Updates
- Branding:
  - `PhysioAI` appears top-left
  - the tagline appears directly below it
- History button is available on:
  - the exercises page (`exercises.html` → `history.html`)
  - the summary page (`summary.html` → `history.html`)

---

## Data Flow (Client → Flask → UI)
1. `session.js` live updates during the session
   - Sends `landmarks` (LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP) + optional `visibility`
   - POSTs to Flask at `/session/update`
2. Flask processes the landmarks
   - Validates required joints
   - Runs exercise logic + session manager to update rep/form metrics
   - Returns JSON containing `feedback`, `current_exercise`, and `metrics`
3. `session.js` ends the session
   - POSTs to `/session/end`
   - Receives back session metrics including:
     - `exercise_breakdown`
     - `exercises`
     - `session_score` (and `overall_score`)
   - Stores the payload in `sessionStorage` for the summary page
4. `summary.js` renders the final metrics table
   - Reads `exercise_breakdown`, `exercises`, and has access to `session_score` from `physioai_session_summary`
   - Uses the exercise breakdown to populate the per-exercise table and compute what’s displayed as the summary score

---

## Key Routes (Flask)
- Auth:
  - `POST /register`
  - `POST /login`
  - `POST /logout`
- Session:
  - `POST /session/start` (enforces exactly 5 selected exercises)
  - `POST /session/update` (joint coords → feedback + rep metrics)
  - `POST /session/end` (final metrics)
- History:
  - `GET /history`
  - `GET /history/<session_id>`

---

*Last updated: March 2026*

# PhysioAI
Smarter Rehab. Better Recovery.

---

## What the project does
PhysioAI is a web app that guides users through physiotherapy exercises using their webcam. Users log in or register, select exactly 5 exercises, and perform them while MediaPipe Pose tracks their key joints in real time. The Flask backend scores reps and movement quality, and the UI shows live feedback during the session. After the session, the final summary page displays a metrics table, and the new Session History page lets users review past performance.

---

## Summary Page Changes (`summary.html` + `frontend/js/summary.js`)
- Shows ONLY the selected exercises for that session.
- Table shows one row per selected exercise with these metrics:
  - Exercise Name
  - Total Reps
  - Correct Reps
  - Incorrect Reps
  - Score (implemented as Posture Correctness %)
- When data is missing, defaults are shown:
  - Overall score displays `0.00 / 100`
  - Table cells use `0` values when rep/metrics fields are absent
- No red/green indicators are used; the table is numerical.

Implementation note (data source):
- `session.js` stores the summary payload in `sessionStorage` under `physioai_session_summary`.
- `summary.js` builds the table using `exercise_breakdown` / `exercises` from that payload, and computes the displayed score from the rep counts for the selected exercises.

---

## Session History Feature (`history.html` + `frontend/js/history.js`)
### What `history.html` does
It displays completed sessions for the user in a simple card layout.

### How sessions are displayed
- Newest to oldest order (history cards are sorted by the session `date` descending).

### What data is shown per session
- Date/time
- Score (stored as `overall_score`)
- Exercises (a list of exercise names performed in that session)

### Where the data comes from (backend vs localStorage fallback)
- Backend persistence exists via Flask endpoints:
  - `GET /history` (list sessions)
  - `GET /history/<session_id>` (session detail)
- Current frontend `history.html` uses a localStorage fallback:
  - `session.js` appends completed sessions into `localStorage` key `physioai_session_history`
  - `history.js` reads and renders from that localStorage data

---

## Frontend Updates
- Branding:
  - `PhysioAI` appears top-left
  - the tagline appears directly below it
- History button is available on:
  - the summary page (`summary.html` → `history.html`)
  - the exercises page (`exercises.html` → `history.html`)

---

## Data Flow (Client → Flask → UI)
1. `session.js` live updates during the session
   - Sends `landmarks` (LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP) + optional `visibility`
   - POSTs to Flask at `/session/update`
2. Flask processes the landmarks
   - Validates required joints
   - Runs exercise logic + session manager to update rep/form metrics
   - Returns JSON containing `feedback`, `current_exercise`, and `metrics` (rep counts and score info)
3. `session.js` ends the session
   - POSTs to `/session/end`
   - Receives back session metrics including:
     - `exercise_breakdown`
     - `exercises`
     - `session_score` (and `overall_score`)
   - Stores the payload in `sessionStorage` for the summary page
4. `summary.js` renders the final metrics table
   - Reads `exercise_breakdown` and `exercises` from `physioai_session_summary`
   - Uses those fields to populate the per-exercise table and compute what’s displayed as the summary score

---

## Key Routes (Flask)
- Auth:
  - `POST /register`
  - `POST /login`
  - `POST /logout`
- Session:
  - `POST /session/start` (enforces exactly 5 selected exercises)
  - `POST /session/update` (joint coords → feedback + rep metrics)
  - `POST /session/end` (final metrics)
- History:
  - `GET /history`
  - `GET /history/<session_id>`

---

*Last updated: March 2026*

*** End of File

## Folder Structure

```
Physio AI - Claude Code/
├── backend/
│   ├── app.py          ← Flask web server (all API routes)
│   ├── auth.py         ← Login/logout helper functions
│   ├── db.py           ← SQLite database helpers
│   └── physioai.db     ← SQLite database file (auto-created)
│
├── utils/
│   ├── pose_module.py      ← Webcam + MediaPipe wrapper (used in console mode)
│   ├── exercise_logic.py   ← All exercise math and rep counting
│   └── session_manager.py  ← Manages 5-exercise session flow
│
├── frontend/
│   ├── index.html          ← Login page
│   ├── exercises.html      ← Exercise selection page
│   ├── session.html        ← Live webcam + feedback page
│   ├── summary.html        ← Final score page
│   ├── css/styles.css      ← All styling
│   └── js/
│       ├── auth.js         ← Login/register JS
│       ├── exercises.js    ← Exercise selection JS
│       ├── session.js      ← Webcam, MediaPipe, and live feedback JS
│       └── summary.js      ← Fetches and displays final score
│
├── main.py             ← Console prototype (not the web app)
└── requirements.txt    ← Python dependencies
```

---

## Backend Files

### `backend/app.py` — The Flask Server
This is the brain of the backend. It defines all the API routes (URL endpoints) that the browser talks to.

**What it does:**
- Starts the Flask web server on port 5000
- Defines these routes:

| Route | Method | What it does |
|---|---|---|
| `/register` | POST | Creates a new user account |
| `/login` | POST | Logs the user in, creates a session |
| `/logout` | POST | Logs the user out |
| `/exercises` | GET | Returns the list of 10 available exercises |
| `/session/start` | POST | Starts a new rehab session with 5 chosen exercises |
| `/session/update` | POST | Receives joint coordinates, returns feedback + rep count |
| `/session/next` | POST | Moves to the next exercise |
| `/session/end` | POST | Ends session, returns final score |

**Key detail:** Active sessions are stored in memory (a Python dictionary), not in the database. If the server restarts, sessions are lost.

---

### `backend/auth.py` — Authentication Helpers
Two simple functions + one decorator.

- `hash_password(password)` — Converts a plain text password into a secure hash using Werkzeug
- `verify_password(hash, password)` — Checks if a password matches a stored hash
- `@login_required` — A decorator applied to any route that needs the user to be logged in. If not logged in, returns a 401 error automatically.

---

### `backend/db.py` — Database Helpers
Handles all communication with the SQLite database.

- `init_db()` — Creates the `users` table if it doesn't exist. Called when the server starts.
- `get_user_by_username(username)` — Looks up a user by username
- `create_user(username, password_hash)` — Inserts a new user into the database

**Database schema (single table):**
```sql
users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  password_hash TEXT,
  created_at TIMESTAMP
)
```

---

## Utils Files

### `utils/exercise_logic.py` — The Exercise Brain
This is the most important and complex file. It contains all the math for detecting whether a user is doing an exercise correctly.

**Key pieces:**

**`calculate_angle(a, b, c)`**
Given 3 points (e.g., shoulder, hip, other hip), computes the angle at point B using the dot product formula. Returns degrees.

**`ExerciseConfig`**
A configuration object for each exercise. Defines:
- Which 3 joints to use
- What angle range counts as a "correct" rep
- Safety limits (angles beyond this are flagged as unsafe)

**`ExerciseState`**
The stateful rep counter. For each exercise:
1. Spends the first 30 frames capturing the user's "neutral" position (baseline)
2. Every frame after that: computes angle deviation from neutral
3. Uses a state machine: tracks when user goes "down" and then "up" to count a rep
4. Marks rep as correct/incorrect based on whether the angle stayed in range

**3 Exercise Types:**
- `angle_based` — Standard three-point angle (most exercises)
- `displacement_based` — Tracks vertical movement (Shoulder Shrugs, Neutral Posture Hold)
- `glute_bridge` / `cobra_pose` — Uses the shoulder-to-hip line angle relative to horizontal (requires side-view camera)

**`ExerciseMetrics`**
Tracks per-exercise stats: total reps, correct reps, incorrect reps, frames in correct posture.

**`default_exercise_configs()`**
Returns a dictionary of all 10 exercises with their angle thresholds pre-defined.

---

### `utils/session_manager.py` — Session Flow
Manages the sequence of 5 exercises in a session.

- `configure_session(exercises)` — Validates and sets up the 5 selected exercises
- `update_with_landmarks(landmarks)` — Called every frame. Passes coordinates to the current exercise's `ExerciseState`, gets back feedback. Auto-advances to next exercise when 10 correct reps are reached.
- `next_exercise()` — Moves to the next exercise. Ends session when all 5 are done.
- `end_session()` — Stops the session and computes the final score.

**Scoring Formula:**
```
Session Score = (0.6 × avg rep accuracy) + (0.4 × avg posture time)
```
- Rep accuracy = correct reps / total reps (max 10 per exercise)
- Posture time = frames in correct position / total frames
- Both averaged across all 5 exercises, then weighted

---

### `utils/pose_module.py` — Webcam Wrapper (Console Mode)
Used only by `main.py` (the console prototype). Not called by the Flask web server.

- Wraps MediaPipe Pose detection
- Supports both old API (MediaPipe 0.9.x) and new API (0.10.x+)
- Reads from webcam, extracts the 4 joints (shoulders + hips), returns a `PoseResult`

In the web app, this role is replaced by MediaPipe.js running in the browser.

---

## Frontend Files

### `frontend/index.html` + `js/auth.js` — Login Page
The first page a user sees. Has a login form and a register form. `auth.js` sends username/password to `/login` or `/register` via fetch API and redirects on success.

---

### `frontend/exercises.html` + `js/exercises.js` — Exercise Selection
Fetches the list of 10 exercises from `/exercises`, displays them as cards. User selects exactly 5. On submit, calls `/session/start` with the selected exercises and redirects to `session.html`.

---

### `frontend/session.html` + `js/session.js` — Live Session (Most Important)
This is the core of the user experience.

**What happens here:**
1. Loads MediaPipe Pose from CDN (runs in browser, no server needed for detection)
2. Opens the webcam
3. Every 250ms: extracts the (x, y) coordinates of the 4 joints from MediaPipe
4. Sends those coordinates to `POST /session/update` as JSON
5. Receives back: feedback text, current exercise name, rep count, score
6. Displays all of that live on screen

**Key detail:** The browser never sends video to the server. It only sends 4 numbers (joint coordinates) per frame. This is why the system is fast and privacy-friendly.

---

### `frontend/summary.html` + `js/summary.js` — Final Score
Calls `POST /session/end` to finalize the session, then displays:
- Overall session score (0–100)
- Per-exercise metrics table (only the selected exercises): total reps, correct reps, incorrect reps, and posture-correctness score (`Score`). When metrics are missing, values default to `0`.

---

### `frontend/css/styles.css` — Styling
All CSS for the app. Uses `.pa-*` class naming convention (PhysioAI prefix). No CSS framework — all custom.

---

## How Flask and the Browser Talk

1. Browser makes a `fetch()` call to `http://localhost:5000/<route>`
2. Sends JSON in the request body
3. Flask processes the request, runs the Python logic, returns JSON
4. Browser reads the JSON and updates the UI

Flask uses cookie-based sessions to remember who is logged in. Every request includes the session cookie automatically via `credentials: "include"` in the fetch calls.

---


