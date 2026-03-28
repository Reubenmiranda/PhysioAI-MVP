from dataclasses import dataclass, field
from typing import Dict, List

from .exercise_logic import (
    ExerciseConfig,
    ExerciseMetrics,
    ExerciseState,
    default_exercise_configs,
)


@dataclass
class SessionMetrics:
    """Aggregated metrics for an entire physiotherapy session."""

    exercises: Dict[str, ExerciseMetrics] = field(default_factory=dict)
    session_score: float = 0.0


class SessionManager:
    """
    Very lightweight session manager for PhysioAI.

    Responsibilities:
    - Holds the fixed catalog of 10 exercises.
    - Accepts a list of 5 selected exercise names.
    - Runs exercises sequentially (the main loop decides when to move on).
    - Aggregates per-exercise metrics and computes a simple session score.
    """

    def __init__(self) -> None:
        self.exercise_catalog: Dict[str, ExerciseConfig] = default_exercise_configs()
        self.selected_exercise_names: List[str] = []
        self.exercise_states: Dict[str, ExerciseState] = {}
        self.current_index: int = 0
        self.session_active: bool = False
        self.metrics = SessionMetrics()

    def configure_session(self, selected_exercises: List[str]) -> None:
        """
        Configure a session with exactly 5 exercises chosen from the catalog.

        Validation is intentionally simple here; in the Flask layer you would
        normally validate user input and handle errors gracefully.
        """
        if len(selected_exercises) != 5:
            raise ValueError("Exactly 5 exercises must be selected for a session.")

        for name in selected_exercises:
            if name not in self.exercise_catalog:
                raise ValueError(f"Unknown exercise selected: {name}")

        self.selected_exercise_names = selected_exercises
        self.exercise_states = {
            name: ExerciseState(self.exercise_catalog[name])
            for name in selected_exercises
        }
        self.current_index = 0
        self.session_active = True
        self.metrics = SessionMetrics()

    def get_current_exercise_name(self) -> str:
        if not self.session_active or not self.selected_exercise_names:
            return ""
        return self.selected_exercise_names[self.current_index]

    def update_with_landmarks(self, landmarks) -> str:
        """
        Update the current exercise with the latest pose landmarks.

        Returns:
            feedback string that can be rendered in the UI.
        """
        if not self.session_active:
            return "Session is not active."

        current_name = self.get_current_exercise_name()
        if not current_name:
            return "No exercise selected."

        state = self.exercise_states[current_name]
        metrics, feedback = state.update(landmarks)

        # Store the latest metrics snapshot
        self.metrics.exercises[current_name] = metrics

        # Auto-advance when the current exercise reaches a score of 10
        # (i.e. 10 correct repetitions). Manual advance via `next_exercise`
        # is still possible from the caller (e.g. key press 'n').
        if metrics.correct_reps >= 10:
            self.next_exercise()

        return feedback

    def next_exercise(self) -> None:
        """
        Move to the next exercise in the selected list.

        In a web application this would typically be triggered either by:
        - A "Next" button press, or
        - A rule such as "after N reps or T seconds".
        Here we just expose the method; the caller decides when to call it.
        """
        if not self.session_active:
            return

        if self.current_index < len(self.selected_exercise_names) - 1:
            self.current_index += 1
        else:
            # End of the list: session is finished
            self.end_session()

    def end_session(self) -> None:
        """Mark the session as finished and compute a simple score."""
        self.session_active = False
        self.metrics.session_score = self._compute_session_score()

    def _compute_session_score(self) -> float:
        """
        Compute a cumulative session score (0-100) based on:
        1. Correct reps / total reps ratio (60% weight)
        2. Posture correctness duration (40% weight)
        
        Score accumulates across ALL exercises in the session.
        Each exercise contributes equally to the final score.
        
        Returns:
            Normalized score from 0.0 to 100.0
        """
        if not self.metrics.exercises:
            return 0.0

        total_reps_score = 0.0
        total_posture_score = 0.0
        exercise_count = len(self.metrics.exercises)

        for m in self.metrics.exercises.values():
            # 1. Rep-based score (60% weight)
            # Cap correct reps at 10 per exercise for scoring
            capped_correct_reps = min(m.correct_reps, 10)
            if m.total_reps > 0:
                # Ratio of correct reps to total reps, normalized to 0-100
                reps_ratio = capped_correct_reps / max(m.total_reps, 10)  # Normalize by max expected (10)
                reps_score = reps_ratio * 100.0
            else:
                reps_score = 0.0
            
            # 2. Posture correctness score (40% weight)
            # Based on time spent in correct posture
            posture_score = m.posture_correctness_ratio * 100.0
            
            # Accumulate scores (will be averaged later)
            total_reps_score += reps_score
            total_posture_score += posture_score

        # Average across all exercises
        avg_reps_score = total_reps_score / exercise_count if exercise_count > 0 else 0.0
        avg_posture_score = total_posture_score / exercise_count if exercise_count > 0 else 0.0

        # Weighted combination: 60% reps, 40% posture
        session_score = (0.6 * avg_reps_score) + (0.4 * avg_posture_score)
        
        # Ensure score is normalized to 0-100
        return max(0.0, min(100.0, session_score))

