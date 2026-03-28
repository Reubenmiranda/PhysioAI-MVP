"""
PhysioAI - Webcam-based physiotherapy session prototype.

This file now acts as a thin entrypoint that wires together:
    - Pose detection (MediaPipe + OpenCV)
    - Exercise logic (joint angles, thresholds, rep counting)
    - A simple session manager (5 selected exercises, sequential flow)

It is intentionally console-based so it can later be wrapped by a Flask
backend and HTML/JS frontend without rewriting the core logic.
"""

import cv2

from utils.pose_module import PoseDetector, overlay_tracking_status
from utils.session_manager import SessionManager
from utils.exercise_logic import default_exercise_configs


def run_console_session() -> None:
    """
    Run a single PhysioAI session using the webcam.

    In the final web version, this function's responsibilities will be
    split across Flask routes (start session, update, end session).
    """
    pose_detector = PoseDetector()
    session = SessionManager()

    # For now we simply auto-select the first 5 exercises from the catalog.
    # In the web app, the user would choose these from a list of 10.
    all_exercises = list(default_exercise_configs().keys())
    selected_exercises = all_exercises[:5]
    session.configure_session(selected_exercises)

    print("Starting PhysioAI console session.")
    print("Selected exercises (5). Each exercise targets 10 correct reps (score 0–10):")
    for name in selected_exercises:
        print(f" - {name}")
    print("Press 'n' to move to the next exercise, 'q' to quit the session.")
    print("The system will automatically move to the next exercise once you reach a score of 10.")

    feedback_text = "Initializing..."

    while True:
        result = pose_detector.read()
        if result is None:
            print("Ignoring empty camera frame.")
            continue

        # Update exercise state only when landmarks are available
        if result.landmarks:
            feedback_text = session.update_with_landmarks(result.landmarks)

        # Overlay tracking and simple textual feedback
        overlay_tracking_status(result.image_bgr, result.pose_detected)
        cv2.putText(
            result.image_bgr,
            feedback_text[:80],  # keep text short for on-screen display
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        current_exercise_name = session.get_current_exercise_name()
        if current_exercise_name:
            # Look up current exercise score (correct reps capped at 10)
            metrics = session.metrics.exercises.get(current_exercise_name)
            current_score = 0
            if metrics is not None:
                current_score = min(metrics.correct_reps, 10)

            cv2.putText(
                result.image_bgr,
                f"Exercise: {current_exercise_name}  Score: {current_score}/10",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.imshow("PhysioAI Pose Session", result.image_bgr)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            # Gracefully end the session
            session.end_session()
            break
        elif key == ord("n"):
            # Move to the next exercise
            session.next_exercise()

        if not session.session_active:
            # All exercises completed
            break

    pose_detector.release()
    cv2.destroyAllWindows()

    # Replace previous per-frame CSV logging with session-level metrics.
    print("Session finished. Summary (non-diagnostic):")
    for name, metrics in session.metrics.exercises.items():
        print(
            f"{name}: score={min(metrics.correct_reps, 10)}/10, "
            f"total_reps={metrics.total_reps}, "
            f"correct_reps={metrics.correct_reps}, "
            f"incorrect_reps={metrics.incorrect_reps}, "
            f"avg_angle_deviation={metrics.average_angle_deviation:.2f}"
        )
    print(
        f"Overall session score (0-100, non-diagnostic): {session.metrics.session_score:.2f}")


if __name__ == "__main__":
    run_console_session()
