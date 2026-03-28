# PhysioAI — Presentation Script

---

## Slide 1 — Title Slide
"This is PhysioAI. Smarter Rehab. Better Recovery.

We built PhysioAI to help people do physiotherapy exercises at home with confidence—using the webcam you already have, and getting guidance while you move."

---

## Slide 2 — Problem Statement
"When people rehab at home, it’s easy to lose the form and control they had in a clinic.

Without real-time feedback, you might not know if your posture is off, if you’re moving too far, or even how many reps you completed correctly."

---

## Slide 3 — Solution Overview
"PhysioAI solves this with AI-based pose tracking in the browser.

Using MediaPipe, the app detects your key joints as you exercise, and it gives you live feedback so you can correct your movement while you train."

---

## Slide 4 — How It Works
"Here’s the simple flow: your webcam captures your pose, MediaPipe detects the key joints, and the frontend sends those joint coordinates to the Flask backend.

The backend scores your reps and form, then the UI updates instantly with feedback as you continue."

---

## Slide 5 — Features
"Now let’s look at what you can do in PhysioAI.

First, there’s a Login and Register system so your sessions are tied to you.

Next, you choose exactly 5 exercises, then start the session. As you perform each exercise, you get real-time feedback—pose guidance and rep counting.

When you finish, you land on a final summary page with a metrics table so you can see how you performed.

And the new Session History feature lets you track past performance over time."

---

## Slide 6 — Tech Stack
"Technically, the frontend is HTML, CSS, and JavaScript, the backend is Flask, and the pose detection runs with MediaPipe Pose in the browser."

---

## Slide 7 — Architecture
"Under the hood, `session.js` sends landmarks and visibility data to Flask through `/session/update`.

Flask runs the exercise logic and session manager, then returns feedback and rep metrics. When the session ends, the backend returns the metrics needed for the summary table, which `summary.js` displays."

---

## Slide 8 — Demo Flow
"So the demo is straightforward: login, select five exercises, perform them with live feedback, and then view your summary score and table.

After that, open Session History to see your newest sessions first—so you can monitor improvement across time."

---

## Slide 9 — Future Improvements
"Looking ahead, we want to expand history so it can be powered directly by the backend for cross-device tracking, and make the scoring explanation even clearer.

With PhysioAI, the goal is simple: help you rehab with better guidance, measure progress, and recover more consistently."

# PhysioAI — Presentation Script

---

## Slide 1 — Title Slide
"This is PhysioAI. Smarter Rehab. Better Recovery.

We built PhysioAI to help people do physiotherapy exercises at home with confidence—using the webcam you already have, and getting guidance while you move."

---

## Slide 2 — Problem Statement
"When people rehab at home, it’s easy to lose the form and control they had in a clinic.

Without real-time feedback, you might not know if your posture is off, if you’re moving too far, or even how many reps you completed correctly."

---

## Slide 3 — Solution Overview
"PhysioAI solves this with AI-based pose tracking in the browser.

Using MediaPipe, the app detects your key joints as you exercise, and it gives you live feedback so you can correct your movement while you train."

---

## Slide 4 — How It Works
"Here’s the simple flow: your webcam captures your pose, MediaPipe detects the key joints, and the frontend sends those joint coordinates to the Flask backend.

The backend scores your reps and form, then the UI updates instantly with feedback as you continue."

---

## Slide 5 — Features
"Now let’s look at what you can do in PhysioAI.

First, there’s a Login and Register system so your sessions are tied to you.

Next, you choose exactly 5 exercises, then start the session. As you perform each exercise, you get real-time feedback—pose guidance and rep counting.

When you finish, you land on a final summary page with a metrics table so you can see how you performed.

And the new Session History feature lets you track past performance over time."

---

## Slide 6 — Tech Stack
"Technically, the frontend is HTML, CSS, and JavaScript, the backend is Flask, and the pose detection runs with MediaPipe Pose in the browser."

---

## Slide 7 — Architecture
"Under the hood, `session.js` sends landmarks and visibility data to Flask through `/session/update`.

Flask runs the exercise logic and session manager, then returns feedback and rep metrics. When the session ends, the backend returns the metrics needed for the summary table, which `summary.js` displays."

---

## Slide 8 — Demo Flow
"So the demo is straightforward: login, select five exercises, perform them with live feedback, and then view your summary score and table.

After that, open Session History to see your newest sessions first—so you can monitor improvement across time."

---

## Slide 9 — Future Improvements
"Looking ahead, we want to expand history so it can be powered directly by the backend for cross-device tracking, and make the scoring explanation even clearer.

With PhysioAI, the goal is simple: help you rehab with better guidance, measure progress, and recover more consistently."

*** End of File

*(As the slide appears, pause for 2–3 seconds, then speak)*

"Good [morning/afternoon]. Today we're presenting PhysioAI — an AI-powered physiotherapy rehabilitation assistant that we built as our major project.

The core idea is simple: use your webcam to guide and score your physiotherapy exercises at home, in real time, with no special hardware.

Let me start by telling you why we built this."

---

## SLIDE 2 — The Problem (Origin Story)

"A couple of years ago, I suffered a spinal injury. I had to go through months of physiotherapy — regular clinic visits, supervised exercises, a lot of waiting around. And eventually, my physiotherapist sent me home with a list of exercises and said: *do these every day.*

But the moment I was home, I was completely on my own. I had no way to know if I was doing the movements correctly. Was my angle right? Was I going too deep? Was I even helping myself or making things worse?

That experience became the seed of this project.

Physiotherapy today is expensive, clinic-dependent, and impossible to self-monitor properly. Patients do exercises at home with zero real-time guidance. PhysioAI was built to change that — to bring guided, scored, real-time feedback directly to the user, at home, through something everyone already has: a webcam."

---

## SLIDE 3 — What Is PhysioAI?

"So what exactly does PhysioAI do?

In the simplest terms: it's a web app that watches you exercise through your webcam and tells you, in real time, whether you're doing it correctly.

Here's the user experience from start to finish.

You open the app in your browser and register an account. You're then shown a catalogue of 10 physiotherapy exercises. You select exactly 5 — whatever is relevant to your rehabilitation — and you begin your session.

The app opens your webcam. You perform each exercise. As you move, you see live feedback on screen: how many reps you've done, how many were correct, and what you should adjust. Once you finish all 5 exercises, you get a final session score from 0 to 100.

What makes this different from just watching a YouTube video? The app is actually watching you back. It's measuring your joint angles against clinically defined thresholds and telling you in real time whether your form is correct. No special equipment required — just a browser and a webcam."

---

## SLIDE 4 — The Technology Stack

"Now let me walk you through the technology stack.

The frontend is built with plain HTML, CSS, and JavaScript — no frontend framework. The pose detection runs in the browser using MediaPipe Pose, which is an open-source AI library from Google, loaded via CDN. This is important — the pose detection runs entirely on the user's device. No video is ever sent to the server.

The backend is a Python Flask application that exposes a REST API. It handles user authentication, session management, and all the exercise scoring logic.

The database is SQLite — lightweight and embedded, no separate database server needed. We use it to store user accounts.

For authentication, we use Flask's built-in session management with Werkzeug for secure password hashing.

The exercise logic — the angle math and rep counting — is entirely custom Python code we wrote ourselves. No third-party AI model is involved in scoring the exercises."

---

## SLIDE 5 — System Architecture

"Let me now show you exactly how all these pieces connect.

When the user is on the session page, MediaPipe Pose is running in their browser, processing the webcam feed at roughly 30 frames per second. From each frame, it extracts the (x, y) coordinates of 4 specific joints: the left shoulder, right shoulder, left hip, and right hip.

Every 250 milliseconds, the browser sends those 4 coordinate pairs — just 8 numbers — to our Flask API via a POST request to `/session/update`.

On the server side, the request first hits `pose_module.py`, which validates that all 4 joints are present and visible with at least 60% confidence. The coordinates then go to `exercise_logic.py`, which calculates the angle at the relevant joint, compares it to the user's neutral baseline, and determines whether a rep is in progress and whether it's correct. `session_manager.py` sits on top of this, managing the sequence of 5 exercises and computing the overall session score.

The server responds with the feedback message, current rep count, and score. The browser displays all of this live.

The key design decision here: we never send video to the server. Only joint coordinates travel over the network. This keeps the system fast, lightweight, and privacy-respecting."

---

## SLIDE 6 — Pose Detection & Exercise Analysis

"Let me go deeper into how the pose detection and exercise analysis actually work.

MediaPipe can detect 33 body landmarks. We only use 4: the two shoulders and the two hips. That's intentional — it keeps the system focused, fast, and reliable.

Before any rep counting begins, the system spends the first 30 frames capturing the user's neutral resting position — the angle their joints are in when standing still. This becomes the baseline. Everything is measured as a deviation from that baseline, which makes the system adaptive to different body types and camera positions.

After that baseline is set, every frame computes the current deviation angle. A state machine tracks when the user moves into the 'down' position and then completes the movement back. When that cycle completes, a rep is counted. The rep is marked correct only if the angle deviation stayed within the clinically defined safe range.

We support 10 exercises in total. Most use this standard three-point angle approach. Two exercises — Shoulder Shrugs and Neutral Posture Hold — use vertical displacement instead of angles. Two exercises — Glute Bridge and Cobra Pose — require a side-view camera and measure the angle of the shoulder-to-hip line relative to the horizontal axis.

Every exercise has its own angle thresholds that were informed by standard physiotherapy range-of-motion guidelines."

---

## SLIDE 7 — Scoring & Real-Time Feedback

"Now let's talk about how the final score is calculated.

The session score is a number from 0 to 100. It's a weighted combination of two things.

60% of the score comes from rep accuracy — how many of your reps were performed correctly, out of the total reps attempted. Each exercise is capped at 10 correct reps for scoring purposes.

40% of the score comes from posture correctness — the fraction of total time you spent in the correct posture range. So even if you're not completing full reps, staying in the right position is rewarded.

Both components are averaged across all 5 exercises, then combined using the 60/40 weighting.

On the feedback side, the system sends back a message every 250 milliseconds. Messages like 'Good posture, continue with controlled movement,' or 'Movement too deep, reduce range for safety,' or 'Repetition looks good, keep breathing.'

One important constraint we built in: all feedback is deliberately non-diagnostic. The app never tells the user what is wrong with their body or suggests a medical conclusion. It only describes the quality of the movement. This is a healthcare safety requirement — PhysioAI is a guidance tool, not a medical device."

---

## SLIDE 8 — Thank You

"To summarize: PhysioAI brings guided, real-time, scored physiotherapy to anyone with a browser and a webcam. It uses MediaPipe for client-side pose detection, custom Python math for exercise analysis, and Flask for the backend API — with no cloud AI, no special hardware, and no video ever leaving the user's device.

This project started from a personal experience of being sent home from physiotherapy with no way to know if I was doing things right. We hope PhysioAI is a step toward solving that.

Thank you. We're happy to take any questions."

---
*End of script*

---

**Presenter Tips:**
- Slide 2 is your most important slide — speak slowly, let the story land
- On Slide 5, point to each box in the flowchart as you mention it
- On Slide 7, say the scoring formula out loud — professors often ask about this
- Total estimated time: 8–10 minutes at a comfortable pace
