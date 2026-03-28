# PhysioAI — Presentation Slides
**Smarter Rehab. Better Recovery.**

---

## Slide 1 — Title Slide
- PhysioAI
- Smarter Rehab. Better Recovery.

---


## Slide 2 — Problem Statement
- Incorrect exercise form when doing rehab at home
- Lack of real-time guidance and progress tracking during sessions
---

## Slide 3 — Solution Overview
- AI-based pose tracking in the browser using MediaPipe
- Live feedback that helps you correct posture and count reps as you exercise

---

## Slide 4 — How It Works
- Webcam captures your pose
- MediaPipe detects key joints (pose detection)
- Frontend sends joint coordinates to the Flask backend
- Backend scores form + reps and returns feedback
- UI updates in real time

---

## Slide 5 — Features
- Login / Register system
- Exercise selection: choose exactly 5 exercises
- Live webcam tracking using MediaPipe
- Real-time feedback (pose + rep counting)
- Final summary page with metrics table
- Session History page (NEW)

---

## Slide 6 — Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- AI: MediaPipe Pose

---

## Slide 7 — Architecture
- Client runs pose detection and extracts required joints
- `session.js` sends landmarks/visibility to Flask (`/session/update`)
- Flask runs exercise logic + session manager
- Flask returns `feedback` and rep metrics to the browser
- On completion, `session.js` calls `/session/end`
- `summary.js` renders the metrics table; history is shown on `history.html`

---

## Slide 8 — Demo Flow
- Login / Register
- Select exactly 5 exercises
- Perform exercises in front of the webcam
- Live feedback + rep counts during the session
- Summary page: view metrics table and session score
- Session History: view past performance (newest → oldest)

---

## Slide 9 — Future Improvements
- Use backend `/history` endpoints to power cross-device history
- Improve the explanation of scoring per exercise (more transparent metrics)
- Add more exercises and exercise-specific guidance
# PhysioAI — Presentation Slides
**Smarter Rehab. Better Recovery.**

---

## Slide 1 — Title Slide
- PhysioAI
- Smarter Rehab. Better Recovery.

---

## Slide 2 — Problem Statement
- Incorrect exercise form when doing rehab at home
- Lack of real-time guidance and progress tracking during sessions

---

## Slide 3 — Solution Overview
- AI-based pose tracking in the browser using MediaPipe
- Live feedback that helps you correct posture and count reps as you exercise

---

## Slide 4 — How It Works
- Webcam captures your pose
- MediaPipe detects key joints (pose detection)
- Frontend sends joint coordinates to the Flask backend
- Backend scores form + reps and returns feedback
- UI updates in real time

---

## Slide 5 — Features
- Login / Register system
- Exercise selection: choose exactly 5 exercises
- Live webcam tracking using MediaPipe
- Real-time feedback (pose + rep counting)
- Final summary page with metrics table
- Session History page (NEW)

---

## Slide 6 — Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- AI: MediaPipe Pose

---

## Slide 7 — Architecture
- Client runs pose detection and extracts required joints
- `session.js` sends landmarks/visibility to Flask (`/session/update`)
- Flask runs exercise logic + session manager
- Flask returns `feedback` and rep metrics to the browser
- On completion, `session.js` calls `/session/end`
- `summary.js` renders the metrics table; history is shown on `history.html`

---

## Slide 8 — Demo Flow
- Login / Register
- Select exactly 5 exercises
- Perform exercises in front of the webcam
- Live feedback + rep counts during the session
- Summary page: view metrics table and session score
- Session History: view past performance (newest → oldest)

---

## Slide 9 — Future Improvements
- Use backend `/history` endpoints to power cross-device history
- Improve the explanation of scoring per exercise (more transparent metrics)
-- Add more exercises and exercise-specific guidance
**Smarter Rehab. Better Recovery.**

---

## Slide 1 — Title Slide
- PhysioAI
- Smarter Rehab. Better Recovery.

---

## Slide 2 — Problem Statement
- Incorrect exercise form when doing rehab at home
- Lack of real-time guidance and progress tracking during sessions

---

## Slide 3 — Solution Overview
- AI-based pose tracking in the browser using MediaPipe
- Live feedback that helps you correct posture and count reps as you exercise

---

## Slide 4 — How It Works
- Webcam captures your pose
- MediaPipe detects key joints (pose detection)
- Frontend sends joint coordinates to the Flask backend
- Backend scores form + reps and returns feedback
- UI updates in real time

---

## Slide 5 — Features
- Login / Register system
- Exercise selection: choose exactly 5 exercises
- Live webcam tracking using MediaPipe
- Real-time feedback (pose + rep counting)
- Final summary page with metrics table
- Session History page (NEW)

---

## Slide 6 — Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- AI: MediaPipe Pose

---

## Slide 7 — Architecture
- Client runs pose detection and extracts required joints
- `session.js` sends landmarks/visibility to Flask (`/session/update`)
- Flask runs exercise logic + session manager
- Flask returns `feedback` and rep metrics to the browser
- On completion, `session.js` calls `/session/end`
- `summary.js` renders the metrics table; history is shown on `history.html`

---

## Slide 8 — Demo Flow
- Login / Register
- Select exactly 5 exercises
- Perform exercises in front of the webcam
- Live feedback + rep counts during the session
- Summary page: view metrics table and session score
- Session History: view past performance (newest → oldest)

---

## Slide 9 — Future Improvements
- Use backend `/history` endpoints to power cross-device history
- Improve the explanation of scoring per exercise (more transparent metrics)
- Add more exercises and exercise-specific guidance

# PhysioAI — Presentation Slides
**Smarter Rehab. Better Recovery.**

---

## Slide 1 — Title Slide
- PhysioAI
- Smarter Rehab. Better Recovery.

---

## Slide 2 — Problem Statement
- Incorrect exercise form when doing rehab at home
- Lack of real-time guidance and progress tracking during sessions

---

## Slide 3 — Solution Overview
- AI-based pose tracking in the browser using MediaPipe
- Live feedback that helps you correct posture and count reps as you exercise

---

## Slide 4 — How It Works
- Webcam captures your pose
- MediaPipe detects key joints (pose detection)
- Frontend sends joint coordinates to the Flask backend
- Backend scores form + reps and returns feedback
- UI updates in real time

---

## Slide 5 — Features
- Login / Register system
- Exercise selection: choose exactly 5 exercises
- Live webcam tracking using MediaPipe
- Real-time feedback (pose + rep counting)
- Final summary page with metrics table
- Session History page (NEW)

---

## Slide 6 — Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- AI: MediaPipe Pose

---

## Slide 7 — Architecture
- Client runs pose detection and extracts required joints
- `session.js` sends landmarks/visibility to Flask (`/session/update`)
- Flask runs exercise logic + session manager
- Flask returns `feedback` and rep metrics to the browser
- On completion, `session.js` calls `/session/end`
- `summary.js` renders the metrics table; history is shown on `history.html`

---

## Slide 8 — Demo Flow
- Login / Register
- Select exactly 5 exercises
- Perform exercises in front of the webcam
- Live feedback + rep counts during the session
- Summary page: view metrics table and session score
- Session History: view past performance (newest → oldest)

---

## Slide 9 — Future Improvements
- Use backend `/history` endpoints to power cross-device history
- Improve the explanation of scoring per exercise (more transparent metrics)
- Add more exercises and exercise-specific guidance

*** End Patch
**8 Slides | Major Project Presentation**

---

## SLIDE 1 — Title Slide

**Heading:** PhysioAI

**Subheading:** An AI-Powered Physiotherapy Rehabilitation Assistant
**Details (small text):**
- [Your Name / Team Name]
- [College Name] | [Department]
- Major Project Presentation | [Date]

---

## SLIDE 2 — The Problem (Origin Story)

**Heading:** Where It Started

**Body (narrative, 2–3 sentences max on slide):**
> "Two years ago, I suffered a spinal injury that required months of physiotherapy. Every session meant travelling to a clinic, waiting, performing exercises under supervision — and the moment I was home, I was on my own. There was no way to know if I was doing the exercises correctly."

**Bullet Points:**
- Physiotherapy is expensive, clinic-dependent, and hard to self-monitor
- Patients perform exercises unsupervised at home — with no feedback on form or progress
- There is no accessible, real-time tool that bridges the gap between clinic and home

**Visual suggestion:** Simple icon or image — person at a webcam vs. person in a clinic

---

## SLIDE 3 — What Is PhysioAI?

**Heading:** What PhysioAI Does

**One-line summary (large text):**
> "A web app that watches you exercise through your webcam and tells you — in real time — whether you're doing it right."

**User Flow (numbered steps):**
1. Register and log in
2. Select exactly 5 exercises from a catalogue of 10
3. Perform each exercise in front of your webcam
4. Receive live feedback: rep count, form correction, posture score
5. Complete all 5 exercises and view your session score (0–100)

**Key Differentiator (callout box):**
No special hardware. No downloads. Just a browser and a webcam.

---

## SLIDE 4 — The Technology Stack

**Heading:** Built With

**Two-column layout:**

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Pose Detection (Client) | MediaPipe Pose (via CDN) |
| Backend / API | Python + Flask |
| Exercise Logic | Custom Python (angle math) |
| Database | SQLite |
| Auth | Flask Sessions + Werkzeug |

**Note (bottom):**
> No cloud AI APIs are used for pose detection — all joint tracking runs locally in the browser via MediaPipe.

---

## SLIDE 5 — System Architecture

**Heading:** How It All Connects — Architecture

**Flowchart (describe for designer):**

```
[Browser / Webcam]
        |
        | MediaPipe.js (runs in browser)
        | Extracts 4 joint coordinates every 250ms
        v
[Flask REST API — localhost:5000]
        |
        | POST /session/update  {landmarks}
        v
[utils/pose_module.py]  →  Validates joints & visibility
        |
        v
[utils/exercise_logic.py]  →  Calculates angle deviation, counts reps
        |
        v
[utils/session_manager.py]  →  Tracks 5-exercise session, computes score
        |
        v
[Flask Response]  →  {feedback, reps, score}
        |
        v
[Browser UI]  →  Displays live feedback to user
        |
        v
[SQLite — physioai.db]  →  Stores user accounts (sessions in memory)
```

**Caption:** All pose processing happens client-side. The backend only receives joint coordinates — not images.

---

## SLIDE 6 — Pose Detection & Exercise Analysis

**Heading:** How the AI Detects and Scores Exercises

**Section A — Pose Detection:**
- MediaPipe tracks **33 body landmarks** but PhysioAI uses only **4 key joints**: Left Shoulder, Right Shoulder, Left Hip, Right Hip
- Each joint must have **≥ 60% visibility confidence** to be valid
- Runs at ~30 FPS directly in the browser — no server round-trip for detection

**Section B — Exercise Analysis (angle-based):**
1. On exercise start → system captures a **neutral reference angle** (averaged over 30 frames)
2. Every frame → measures **deviation from that neutral angle**
3. Rep is counted when the user moves through the full range and returns to neutral
4. Rep is marked **correct** only if the angle stays within the clinically defined safe range

**10 Exercises supported** — each with its own angle thresholds:
- Angle-based: Hip Flexion, Trunk Side Bend, Forward/Lateral Arm Raise, Arm Circles, Standing March
- Displacement-based: Shoulder Shrugs, Neutral Posture Hold
- Side-view (shoulder-hip line): Glute Bridge, Cobra Pose

---

## SLIDE 7 — Scoring & Real-Time Feedback

**Heading:** Scoring System & Live Feedback

**Scoring Formula:**
```
Session Score (0–100) =
    (0.6 × Average Rep Accuracy Score)
  + (0.4 × Average Posture Correctness Score)
```

- **Rep Score** = Correct reps ÷ Total reps × 100 (capped at 10 reps per exercise)
- **Posture Score** = Frames in correct position ÷ Total frames × 100
- Averaged across all 5 exercises, then weighted

**Real-Time Feedback (examples):**
- "Good posture. Continue with controlled movement."
- "Movement too deep. Reduce range for safety."
- "Repetition looks good. Keep breathing and avoid pain."

**Safety Constraint:**
> All feedback is deliberately non-diagnostic. The app never suggests a medical conclusion — it only describes movement quality.

---

## SLIDE 8 — Thank You

**Heading:** Thank You

**Subheading:** PhysioAI — Bringing Guided Rehabilitation Home

**Body (optional):**
> Built with Python, Flask, MediaPipe, and a belief that good physiotherapy shouldn't end when you leave the clinic.

**Details:**
- [Your Name / Team]
- [GitHub link or demo link if applicable]

**Bottom line:**
> Questions Welcome

---
*End of slides*
