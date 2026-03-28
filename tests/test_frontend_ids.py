"""
ID verification tests for PhysioAI frontend HTML files.
Each test checks that required element IDs exist in the HTML.
These tests FAIL before implementation and PASS after.
"""
from html.parser import HTMLParser
import os

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")


class IDCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" and value:
                self.ids.add(value)
            if name == "class" and value:
                for cls in value.split():
                    self.classes.add(cls)


def get_ids_and_classes(filename):
    path = os.path.join(FRONTEND, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Frontend HTML file not found: {path}. "
            "Ensure 'frontend/' is present relative to the project root."
        )
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parser = IDCollector()
    parser.feed(content)
    return parser.ids, parser.classes


def test_login_ids():
    ids, _ = get_ids_and_classes("index.html")
    for required in ["login-form", "email", "password", "error"]:
        assert required in ids, f"index.html missing id='{required}'"


def test_signup_ids():
    ids, _ = get_ids_and_classes("signup.html")
    for required in ["signup-form", "name", "email", "age", "gender", "password", "confirm", "error"]:
        assert required in ids, f"signup.html missing id='{required}'"


def test_exercises_ids():
    ids, _ = get_ids_and_classes("exercises.html")
    for required in ["exercise-list", "start-session-btn", "session-history-btn", "exercise-helper", "exercises-message"]:
        assert required in ids, f"exercises.html missing id='{required}'"
    # Note: exercise-checkbox class is created dynamically by exercises.js at runtime.
    # It is NOT in the static HTML (exercise-list container is empty after adaptation).
    # This class is verified by browser testing, not by this static parser test.


def test_session_ids():
    ids, _ = get_ids_and_classes("session.html")
    for required in [
        "video", "output-canvas", "camera-status",
        "current-exercise", "feedback-text", "rep-stats",
        "next-exercise-btn", "end-session-btn", "session-message",
        "correctSound", "wrongSound"
    ]:
        assert required in ids, f"session.html missing id='{required}'"


def test_summary_ids():
    ids, _ = get_ids_and_classes("summary.html")
    for required in ["overall-score", "total-reps", "summary-table", "summary-message"]:
        assert required in ids, f"summary.html missing id='{required}'"


def test_history_ids():
    ids, _ = get_ids_and_classes("history.html")
    for required in ["history-list", "history-message"]:
        assert required in ids, f"history.html missing id='{required}'"
