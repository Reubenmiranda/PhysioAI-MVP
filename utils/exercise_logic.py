import math
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional


Point = Tuple[float, float]


def calculate_angle(a: Point, b: Point, c: Point) -> float:
    """
    Calculate the angle (in degrees) at point B given three points A-B-C.

    Uses the cosine rule on vectors BA and BC. This is reusable for
    shoulders, hips, knees, etc. Coordinates are expected to be
    normalized image coordinates (0-1) as returned by MediaPipe.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c

    # Vectors BA and BC
    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)

    # Dot product and magnitudes
    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)

    if mag_ba == 0 or mag_bc == 0:
        # Degenerate case: points collapsed, treat as neutral angle
        return 0.0

    cos_theta = max(min(dot_product / (mag_ba * mag_bc), 1.0), -1.0)
    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


@dataclass
class ExerciseConfig:
    """
    Configuration for an individual physiotherapy exercise.

    The same rep-counting logic is reused for all exercises; only the
    target joint, angle thresholds and naming differ.
    """

    name: str
    # Names of the three joints used for the angle calculation (A-B-C)
    joint_a: str
    joint_b: str
    joint_c: str
    # Angle thresholds in degrees (relative to neutral reference)
    min_angle_down: float  # Minimum deviation from neutral for "down" position
    max_angle_up: float  # Maximum deviation from neutral for "up" position
    # Correct range: deviation from neutral that counts as correct
    correct_range_min: float  # Minimum deviation for correct rep
    # Maximum deviation for correct rep (safety bound)
    correct_range_max: float
    # How far the angle is allowed to deviate from ideal at the end of a rep.
    max_deviation_deg: float = 15.0
    # Margin used for detecting the top of the movement
    safety_margin_deg: float = 5.0
    # Number of frames to capture neutral reference (for stability)
    neutral_capture_frames: int = 30
    # Exercise type: 'angle_based' (uses angle calculation) or 'displacement_based' (uses vertical displacement)
    exercise_type: str = 'angle_based'


@dataclass
class ExerciseMetrics:
    """Aggregated metrics for a single exercise within a session."""

    exercise_name: str
    total_reps: int = 0
    # We treat "correct_reps" as the exercise's score as well,
    # capped at 10 points per exercise.
    correct_reps: int = 0
    incorrect_reps: int = 0
    angle_sum: float = 0.0
    angle_count: int = 0
    # Track time spent in correct posture (in frames)
    correct_posture_frames: int = 0
    total_frames: int = 0

    @property
    def average_angle(self) -> float:
        return self.angle_sum / self.angle_count if self.angle_count > 0 else 0.0

    @property
    def average_angle_deviation(self) -> float:
        # This can be refined per-exercise if needed
        return self.average_angle

    @property
    def posture_correctness_ratio(self) -> float:
        """Ratio of time spent in correct posture (0.0 to 1.0)"""
        return self.correct_posture_frames / self.total_frames if self.total_frames > 0 else 0.0


def calculate_vertical_displacement(point1: Point, point2: Point) -> float:
    """
    Calculate vertical displacement between two points.
    Returns positive value if point1 is above point2.
    """
    return point1[1] - point2[1]


def calculate_angle_to_horizontal(point1: Point, point2: Point) -> float:
    """
    Calculate the angle (in degrees) between the line from point1 to point2
    and the horizontal axis.

    For side-view glute bridge:
    - point1: shoulder position
    - point2: hip position
    - Returns angle in degrees (0° = horizontal, 90° = vertical)
    - Smaller angle = hip elevated (bridge position)
    - Larger angle = hip low (neutral/supine position)

    NOTE: This assumes side-view camera perspective where the horizontal
    axis corresponds to the x-axis in normalized coordinates.
    """
    x1, y1 = point1
    x2, y2 = point2

    # Vector from shoulder to hip
    dx = x2 - x1
    dy = y2 - y1

    # Handle degenerate case
    if abs(dx) < 1e-6:
        # Vertical line
        return 90.0

    # Calculate angle using atan2, then convert to degrees
    # atan2(dy, dx) gives angle from horizontal
    angle_rad = math.atan2(abs(dy), abs(dx))
    angle_deg = math.degrees(angle_rad)

    return angle_deg


class ExerciseState:
    """
    Stateful rep counter for a single exercise with neutral reference tracking.

    Key improvements:
    - Captures neutral reference angle at exercise start
    - Computes angles as deviation from neutral
    - Enforces strict safety bounds to prevent excessive depth
    - Tracks posture correctness duration for scoring
    """

    def __init__(self, config: ExerciseConfig) -> None:
        self.config = config
        self.metrics = ExerciseMetrics(exercise_name=config.name)
        self._in_down_position = False
        # Neutral reference tracking
        self._neutral_angle: Optional[float] = None
        self._neutral_displacement: Optional[float] = None
        self._neutral_samples: list = []
        self._neutral_captured = False

    def _capture_neutral_reference(self, angle: Optional[float] = None, displacement: Optional[float] = None) -> None:
        """Capture neutral reference over multiple frames for stability."""
        if self._neutral_captured:
            return

        if angle is not None:
            self._neutral_samples.append(angle)
        elif displacement is not None:
            self._neutral_samples.append(displacement)

        if len(self._neutral_samples) >= self.config.neutral_capture_frames:
            # Use median for robustness against outliers
            sorted_samples = sorted(self._neutral_samples)
            median_idx = len(sorted_samples) // 2
            if angle is not None:
                self._neutral_angle = sorted_samples[median_idx]
            else:
                self._neutral_displacement = sorted_samples[median_idx]
            self._neutral_captured = True
            self._neutral_samples.clear()

    def update(self, landmarks: Dict[str, Point]) -> Tuple[ExerciseMetrics, str]:
        """
        Update state based on the latest landmarks.

        Returns:
            (metrics, feedback_text)
        """
        a = landmarks.get(self.config.joint_a)
        b = landmarks.get(self.config.joint_b)
        c = landmarks.get(self.config.joint_c)

        if a is None or b is None or c is None:
            return self.metrics, "Unable to clearly see required joints. Please face the camera."

        self.metrics.total_frames += 1

        # Handle different exercise types
        if self.config.exercise_type == 'displacement_based':
            # For exercises like Shoulder Shrugs and Neutral Posture Hold
            if self.config.name == "Shoulder Shrugs":
                # Vertical displacement of shoulders relative to hips
                left_displacement = calculate_vertical_displacement(
                    landmarks.get("LEFT_SHOULDER", (0, 0)),
                    landmarks.get("LEFT_HIP", (0, 0))
                )
                right_displacement = calculate_vertical_displacement(
                    landmarks.get("RIGHT_SHOULDER", (0, 0)),
                    landmarks.get("RIGHT_HIP", (0, 0))
                )
                displacement = (left_displacement + right_displacement) / 2.0

                if not self._neutral_captured:
                    self._capture_neutral_reference(displacement=displacement)
                    return self.metrics, f"{self.config.name}: Establishing baseline. Stand naturally."

                deviation = displacement - self._neutral_displacement

                # Track peak elevation during movement
                if not hasattr(self, '_peak_elevation'):
                    self._peak_elevation = 0.0

                # Rep counting: detect elevation then return to neutral
                if not self._in_down_position:
                    if deviation > 0.02:  # Start of elevation
                        self._in_down_position = True
                        self._peak_elevation = deviation
                        feedback = f"{self.config.name}: Elevating shoulders. Keep it controlled."
                    else:
                        # Correct range: near neutral
                        if -0.01 <= deviation <= 0.01:
                            self.metrics.correct_posture_frames += 1
                            feedback = f"{self.config.name}: Good posture. Stand naturally."
                        else:
                            feedback = f"{self.config.name}: Maintain neutral posture."
                else:
                    # During elevation phase
                    if deviation > self._peak_elevation:
                        self._peak_elevation = deviation

                    # Check if returned to neutral
                    if -0.01 <= deviation <= 0.01:
                        self.metrics.total_reps += 1
                        self._in_down_position = False
                        # Check if peak elevation was in correct range (0.02 to 0.05)
                        if 0.02 <= self._peak_elevation <= 0.05:
                            self.metrics.correct_reps += 1
                            feedback = f"{self.config.name}: Good repetition. Keep it controlled."
                        else:
                            self.metrics.incorrect_reps += 1
                            feedback = f"{self.config.name}: Try to maintain smoother, controlled movement."
                        self._peak_elevation = 0.0
                    elif deviation > 0.05:
                        # Excessive elevation - warn but don't invalidate yet
                        feedback = f"{self.config.name}: Reduce elevation. Keep movement controlled."
                    else:
                        feedback = f"{self.config.name}: Elevating shoulders. Return to neutral slowly."

                return self.metrics, feedback

            elif self.config.name == "Neutral Posture Hold":
                # Shoulder-hip vertical alignment
                left_alignment = abs(calculate_vertical_displacement(
                    landmarks.get("LEFT_SHOULDER", (0, 0)),
                    landmarks.get("LEFT_HIP", (0, 0))
                ))
                right_alignment = abs(calculate_vertical_displacement(
                    landmarks.get("RIGHT_SHOULDER", (0, 0)),
                    landmarks.get("RIGHT_HIP", (0, 0))
                ))
                avg_alignment = (left_alignment + right_alignment) / 2.0

                if not self._neutral_captured:
                    self._capture_neutral_reference(displacement=avg_alignment)
                    return self.metrics, f"{self.config.name}: Establishing baseline. Stand upright."

                deviation = abs(avg_alignment - self._neutral_displacement)
                # Correct: deviation < 5% (approximately 5 degrees)
                if deviation < 0.05:
                    self.metrics.correct_posture_frames += 1
                    feedback = f"{self.config.name}: Excellent posture. Hold this position."
                else:
                    feedback = f"{self.config.name}: Adjust your posture. Keep shoulders aligned with hips."

                return self.metrics, feedback

        # Handle Glute Bridge (special angle calculation: shoulder-hip line to horizontal)
        if self.config.exercise_type == 'glute_bridge':
            # For glute bridge, calculate angle between shoulder-hip line and horizontal
            # This assumes side-view camera where horizontal axis is meaningful
            angle = calculate_angle_to_horizontal(a, b)  # shoulder (a) to hip (b)

            # Capture neutral reference if not yet captured
            if not self._neutral_captured:
                self._capture_neutral_reference(angle=angle)
                return self.metrics, f"{self.config.name}: Establishing baseline. Lie supine with hips low."

            # For glute bridge, we work with absolute angles (not deviation from neutral)
            # Neutral position: 40°-60° (back and spine in line, hip low)
            # Bridge position: 15°-35° (hip elevated, around 30° is typical)

            # Accumulate for average statistics
            self.metrics.angle_sum += angle
            self.metrics.angle_count += 1

            # Check if within correct posture range (more forgiving)
            in_correct_range = (
                self.config.correct_range_min <= angle <= self.config.correct_range_max
            )
            if in_correct_range:
                self.metrics.correct_posture_frames += 1

            # Safety check: prevent excessive arching only
            if angle < 10.0:
                feedback = (
                    f"{self.config.name}: Excessive arching detected. Reduce elevation for safety. "
                    "If you feel discomfort, stop immediately."
                )
                return self.metrics, feedback

            feedback = f"{self.config.name}: Maintain a slow and controlled motion."

            # Rep counting state machine for glute bridge (more forgiving)
            # Rep starts in neutral (40°-60°), moves to bridge (15°-35°), returns to neutral
            # Use wider ranges to be less strict about exact angles

            # Neutral position: 40° and above (back and spine in line)
            if angle >= self.config.min_angle_down:
                # User is in neutral/supine position
                if self._in_down_position:
                    # Returned to neutral from bridge position -> count a rep
                    self.metrics.total_reps += 1
                    self._in_down_position = False

                    # Check correctness: must have reached bridge position during the rep
                    # More forgiving - any significant elevation counts
                    if self._reached_bridge_position:
                        self.metrics.correct_reps += 1
                        feedback = (
                            f"{self.config.name}: Repetition looks good. Keep breathing and avoid pain."
                        )
                    else:
                        self.metrics.incorrect_reps += 1
                        feedback = (
                            f"{self.config.name}: Try to elevate hips more to complete the bridge. "
                            "If you feel discomfort, please stop and consult a professional."
                        )
                    self._reached_bridge_position = False
                else:
                    # In neutral, ready to start next rep
                    feedback = f"{self.config.name}: Good neutral position. Elevate hips to start."

            # Bridge position: any angle significantly less than neutral (more forgiving)
            # Accept angles from 15° up to 40° (allows typical 30° lifts)
            elif angle <= 40.0:
                # User is in bridge position (elevated)
                self._in_down_position = True
                # Mark as reached bridge if in the ideal range (15°-35°)
                if self.config.correct_range_min <= angle <= self.config.correct_range_max:
                    self._reached_bridge_position = True
                # Also accept if close to ideal range (10°-40°)
                elif 10.0 <= angle <= 40.0:
                    self._reached_bridge_position = True

                feedback = f"{self.config.name}: Good bridge position. Hold briefly, then lower slowly."
            else:
                # Transitioning between positions (angle between 40° and min_angle_down)
                if self._in_down_position:
                    # Was in bridge, now moving toward neutral
                    feedback = f"{self.config.name}: Lowering hips. Return to neutral position slowly."
                else:
                    # Moving from neutral toward bridge
                    feedback = f"{self.config.name}: Elevating hips. Continue to bridge position."

            return self.metrics, feedback

        elif self.config.exercise_type == 'cobra_pose':
            # Cobra pose (prone back extension) uses shoulder-hip line to horizontal
            angle = calculate_angle_to_horizontal(a, b)

            # Capture neutral reference for deviation metrics only
            if not self._neutral_captured:
                self._capture_neutral_reference(angle=angle)
                return self.metrics, f"{self.config.name}: Establishing baseline. Lie prone and stay relaxed."

            angle_deviation = angle - self._neutral_angle
            self.metrics.angle_sum += angle_deviation
            self.metrics.angle_count += 1

            # Initialize state tracking for cobra-specific logic
            if not hasattr(self, "_cobra_peak"):
                self._cobra_peak = 0.0
                self._cobra_in_lift = False
                self._cobra_invalid_rep = False

            # Safety: overextension
            if angle > 50.0:
                self._cobra_invalid_rep = True
                feedback = f"{self.config.name}: Avoid overextending your back. Ease down slowly."
            else:
                feedback = f"{self.config.name}: Move slowly and keep hips grounded."

            # Detect start position (neutral 5°–15°)
            in_neutral = 5.0 <= angle <= 15.0
            in_target_lift = 25.0 <= angle <= 45.0

            if not self._cobra_in_lift:
                if in_neutral:
                    self._cobra_peak = angle
                    self._cobra_invalid_rep = False
                    feedback = f"{self.config.name}: Good start position. Lift chest gently using your arms."
                elif angle >= 20.0:
                    # Begin lift once angle clearly increases
                    self._cobra_in_lift = True
                    self._cobra_peak = angle
                    self._cobra_invalid_rep = angle > 50.0
                    feedback = f"{self.config.name}: Lifting. Keep the motion small and controlled."
                else:
                    feedback = f"{self.config.name}: Lift slightly higher to start the cobra pose."
            else:
                # During lift/hold
                self._cobra_peak = max(self._cobra_peak, angle)
                if angle <= 15.0:
                    # Returned to neutral -> evaluate rep
                    self.metrics.total_reps += 1
                    self._cobra_in_lift = False
                    peak = self._cobra_peak
                    invalid = self._cobra_invalid_rep
                    self._cobra_peak = 0.0
                    self._cobra_invalid_rep = False

                    if invalid or peak > 50.0:
                        self.metrics.incorrect_reps += 1
                        feedback = f"{self.config.name}: Avoid overextending your back. Keep lifts small."
                    elif peak < 20.0:
                        self.metrics.incorrect_reps += 1
                        feedback = f"{self.config.name}: Lift slightly higher for a full repetition."
                    elif 25.0 <= peak <= 45.0:
                        self.metrics.correct_reps += 1
                        feedback = f"{self.config.name}: Nice controlled lift. Lower slowly."
                    else:
                        self.metrics.incorrect_reps += 1
                        feedback = f"{self.config.name}: Keep the lift gentle (25°–45°)."
                else:
                    if angle < 25.0:
                        feedback = f"{self.config.name}: Lift slightly higher, stay comfortable."
                    elif in_target_lift:
                        feedback = f"{self.config.name}: Good control. Hold briefly, then lower with control."
                    elif angle > 45.0:
                        feedback = f"{self.config.name}: Avoid overextending your back. Ease down slightly."

            # Posture correctness tracking: only count time in safe target band
            if in_target_lift and not self._cobra_invalid_rep:
                self.metrics.correct_posture_frames += 1

            return self.metrics, feedback

            # Capture neutral reference if not yet captured
            if not self._neutral_captured:
                self._capture_neutral_reference(angle=angle)
                return self.metrics, f"{self.config.name}: Establishing baseline. Lie supine with hips low."

            # For glute bridge, we work with absolute angles (not deviation from neutral)
            # Neutral position: 40°-60° (back and spine in line, hip low)
            # Bridge position: 15°-35° (hip elevated, around 30° is typical)

            # Accumulate for average statistics
            self.metrics.angle_sum += angle
            self.metrics.angle_count += 1

            # Check if within correct posture range (more forgiving)
            in_correct_range = (
                self.config.correct_range_min <= angle <= self.config.correct_range_max
            )
            if in_correct_range:
                self.metrics.correct_posture_frames += 1

            # Safety check: prevent excessive arching only
            if angle < 10.0:
                feedback = (
                    f"{self.config.name}: Excessive arching detected. Reduce elevation for safety. "
                    "If you feel discomfort, stop immediately."
                )
                return self.metrics, feedback

            feedback = f"{self.config.name}: Maintain a slow and controlled motion."

            # Rep counting state machine for glute bridge (more forgiving)
            # Rep starts in neutral (40°-60°), moves to bridge (15°-35°), returns to neutral
            # Use wider ranges to be less strict about exact angles

            # Neutral position: 40° and above (back and spine in line)
            if angle >= self.config.min_angle_down:
                # User is in neutral/supine position
                if self._in_down_position:
                    # Returned to neutral from bridge position -> count a rep
                    self.metrics.total_reps += 1
                    self._in_down_position = False

                    # Check correctness: must have reached bridge position during the rep
                    # More forgiving - any significant elevation counts
                    if self._reached_bridge_position:
                        self.metrics.correct_reps += 1
                        feedback = (
                            f"{self.config.name}: Repetition looks good. Keep breathing and avoid pain."
                        )
                    else:
                        self.metrics.incorrect_reps += 1
                        feedback = (
                            f"{self.config.name}: Try to elevate hips more to complete the bridge. "
                            "If you feel discomfort, please stop and consult a professional."
                        )
                    self._reached_bridge_position = False
                else:
                    # In neutral, ready to start next rep
                    feedback = f"{self.config.name}: Good neutral position. Elevate hips to start."

            # Bridge position: any angle significantly less than neutral (more forgiving)
            # Accept angles from 15° up to 40° (allows typical 30° lifts)
            elif angle <= 40.0:
                # User is in bridge position (elevated)
                self._in_down_position = True
                # Mark as reached bridge if in the ideal range (15°-35°)
                if self.config.correct_range_min <= angle <= self.config.correct_range_max:
                    self._reached_bridge_position = True
                # Also accept if close to ideal range (10°-40°)
                elif 10.0 <= angle <= 40.0:
                    self._reached_bridge_position = True

                feedback = f"{self.config.name}: Good bridge position. Hold briefly, then lower slowly."
            else:
                # Transitioning between positions (angle between 40° and min_angle_down)
                if self._in_down_position:
                    # Was in bridge, now moving toward neutral
                    feedback = f"{self.config.name}: Lowering hips. Return to neutral position slowly."
                else:
                    # Moving from neutral toward bridge
                    feedback = f"{self.config.name}: Elevating hips. Continue to bridge position."

            return self.metrics, feedback

        # Standard angle-based exercises (three-point angle calculation)
        angle = calculate_angle(a, b, c)

        # Capture neutral reference if not yet captured
        if not self._neutral_captured:
            self._capture_neutral_reference(angle=angle)
            return self.metrics, f"{self.config.name}: Establishing baseline. Stand in neutral position."

        # Calculate deviation from neutral
        angle_deviation = angle - self._neutral_angle

        # Accumulate for average statistics
        self.metrics.angle_sum += angle_deviation
        self.metrics.angle_count += 1

        # Check if within correct posture range
        in_correct_range = (
            self.config.correct_range_min <= angle_deviation <= self.config.correct_range_max
        )
        if in_correct_range:
            self.metrics.correct_posture_frames += 1

        # Safety check: invalidate if beyond safe range
        if angle_deviation > self.config.correct_range_max:
            feedback = (
                f"{self.config.name}: Movement too deep. Reduce range for safety. "
                "If you feel discomfort, stop immediately."
            )
            return self.metrics, feedback

        feedback = f"{self.config.name}: Maintain a slow and controlled motion."

        # Rep counting state machine (using deviation from neutral)
        if angle_deviation < self.config.min_angle_down:
            # User is in the "down" position
            self._in_down_position = True
            feedback = f"{self.config.name}: Good start position. Now extend slowly."
        elif (
            self._in_down_position
            and angle_deviation > self.config.max_angle_up + self.config.safety_margin_deg
        ):
            # User has moved from down to up -> count a rep
            self.metrics.total_reps += 1
            self._in_down_position = False

            # Check correctness: must be within correct range and not exceed safety bounds
            if (
                self.config.correct_range_min <= angle_deviation <= self.config.correct_range_max
                and abs(angle_deviation - self.config.max_angle_up) <= self.config.max_deviation_deg
            ):
                self.metrics.correct_reps += 1
                feedback = (
                    f"{self.config.name}: Repetition looks good. Keep breathing and avoid pain."
                )
            else:
                self.metrics.incorrect_reps += 1
                feedback = (
                    f"{self.config.name}: Try to keep your movement smoother and within safe range. "
                    "If you feel discomfort, please stop and consult a professional."
                )
        else:
            # Neutral movement zone
            if in_correct_range:
                feedback = (
                    f"{self.config.name}: Good posture. Continue with controlled movement."
                )
            else:
                feedback = (
                    f"{self.config.name}: Move gently. Stop if anything feels painful or unsafe."
                )

        return self.metrics, feedback


def default_exercise_configs() -> Dict[str, ExerciseConfig]:
    """
    Provide a fixed set of 10 standing physiotherapy exercises.

    All exercises use ONLY shoulder and hip joints as per project constraints.
    Angles are computed as deviations from a neutral reference captured at exercise start.

    NOTE: These are demonstration-only and are intentionally conservative.
    They DO NOT constitute medical advice or diagnosis.
    """
    return {
        # 1. Standing Hip Flexion
        # Angle: Shoulder-Hip-OtherHip (detects forward lean)
        # Correct range: +20° to +45° from neutral (hip flexion forward)
        "Standing Hip Flexion": ExerciseConfig(
            name="Standing Hip Flexion",
            joint_a="LEFT_SHOULDER",
            joint_b="LEFT_HIP",
            joint_c="RIGHT_HIP",
            min_angle_down=-5.0,  # Below neutral
            max_angle_up=20.0,  # Target flexion
            correct_range_min=20.0,  # Minimum correct flexion
            correct_range_max=45.0,  # Maximum safe flexion (safety bound)
            max_deviation_deg=10.0,
            exercise_type='angle_based',
        ),

        # 2. Glute Bridge (Side View)
        # Exercise: Supine glute bridge captured from fixed side-view camera
        # Metric: Shoulder-hip line orientation relative to horizontal
        # Neutral position (supine): 40°-60° (hip low, back and spine in line)
        # Correct bridge position: 15°-35° (hip elevated, around 30° is typical)
        # Safety: Prevents excessive arching (angle < 10°)
        #
        # NOTE: This exercise uses a special angle calculation (shoulder-hip to horizontal)
        # rather than the standard three-point angle. The side-view assumption allows
        # shoulder-hip orientation to accurately represent hip elevation without knee tracking.
        "Glute Bridge": ExerciseConfig(
            name="Glute Bridge",
            joint_a="LEFT_SHOULDER",  # Used for shoulder-hip line calculation
            joint_b="LEFT_HIP",  # Used for shoulder-hip line calculation
            joint_c="RIGHT_HIP",  # Not used for angle, but required by interface
            # Neutral/supine position (back and spine in line)
            min_angle_down=40.0,
            max_angle_up=35.0,  # Bridge position threshold (hip elevated)
            correct_range_min=15.0,  # Minimum correct bridge elevation
            # Maximum safe bridge elevation (allows up to 35° for typical 30° lifts)
            correct_range_max=35.0,
            max_deviation_deg=10.0,  # More forgiving tolerance for bridge position
            exercise_type='glute_bridge',  # Special exercise type
        ),

        # 3. Cobra Pose (Prone Back Extension, side view)
        # Uses shoulder-hip line to horizontal; hips stay down, lift is small.
        # Neutral: 5°-15°; Target lift: 25°-45°; Overextension: >50° invalid.
        "Cobra Pose": ExerciseConfig(
            name="Cobra Pose",
            joint_a="LEFT_SHOULDER",  # Shoulder for shoulder-hip line
            joint_b="LEFT_HIP",       # Hip for shoulder-hip line
            joint_c="RIGHT_HIP",      # Not used but kept for interface consistency
            min_angle_down=15.0,      # Neutral threshold upper bound
            max_angle_up=25.0,        # Entry to lifted range
            correct_range_min=25.0,   # Minimum correct lift
            correct_range_max=45.0,   # Maximum safe lift
            max_deviation_deg=5.0,
            safety_margin_deg=5.0,
            exercise_type='cobra_pose',
        ),

        # 4. Standing March (Low Knee Lift)
        # Angle: Shoulder-Hip-OtherHip (detects controlled hip flexion)
        # Correct range: 20°-40° from neutral
        "Standing March": ExerciseConfig(
            name="Standing March",
            joint_a="LEFT_SHOULDER",
            joint_b="LEFT_HIP",
            joint_c="RIGHT_HIP",
            min_angle_down=-5.0,  # Neutral
            max_angle_up=20.0,  # Target lift
            correct_range_min=20.0,  # Minimum lift
            correct_range_max=40.0,  # Maximum safe lift
            max_deviation_deg=10.0,
            exercise_type='angle_based',
        ),

        # 5. Standing Forward Arm Raise
        # Angle: Hip-Shoulder-OtherShoulder (detects shoulder flexion)
        # Correct range: 70°-100° (shoulder flexion)
        "Standing Forward Arm Raise": ExerciseConfig(
            name="Standing Forward Arm Raise",
            joint_a="LEFT_HIP",
            joint_b="LEFT_SHOULDER",
            joint_c="RIGHT_SHOULDER",
            min_angle_down=0.0,  # Arms by side
            max_angle_up=70.0,  # Target flexion
            correct_range_min=70.0,  # Minimum flexion
            correct_range_max=100.0,  # Maximum safe flexion
            max_deviation_deg=15.0,
            exercise_type='angle_based',
        ),

        # 6. Standing Lateral Arm Raise
        # Angle: Hip-Shoulder-OtherShoulder (detects shoulder abduction)
        # Correct range: 70°-100° (shoulder abduction)
        "Standing Lateral Arm Raise": ExerciseConfig(
            name="Standing Lateral Arm Raise",
            joint_a="LEFT_HIP",
            joint_b="LEFT_SHOULDER",
            joint_c="RIGHT_SHOULDER",
            min_angle_down=0.0,  # Arms by side
            max_angle_up=70.0,  # Target abduction
            correct_range_min=70.0,  # Minimum abduction
            correct_range_max=100.0,  # Maximum safe abduction
            max_deviation_deg=15.0,
            exercise_type='angle_based',
        ),

        # 7. Shoulder Shrugs
        # Metric: Vertical displacement of shoulders relative to hips
        # Uses displacement-based tracking
        "Shoulder Shrugs": ExerciseConfig(
            name="Shoulder Shrugs",
            joint_a="LEFT_SHOULDER",  # Not used for angle, but required
            joint_b="LEFT_HIP",
            joint_c="RIGHT_HIP",
            min_angle_down=0.0,  # Not used for displacement-based
            max_angle_up=0.0,  # Not used for displacement-based
            correct_range_min=0.0,  # Not used
            correct_range_max=0.0,  # Not used
            exercise_type='displacement_based',
        ),

        # 8. Standing Trunk Side Bend (Small Range)
        # Angle: Shoulder-Hip-OtherHip (detects lateral trunk deviation)
        # Correct range: 10°-25° deviation (hard limit: >25° = unsafe)
        "Standing Trunk Side Bend": ExerciseConfig(
            name="Standing Trunk Side Bend",
            joint_a="LEFT_SHOULDER",
            joint_b="LEFT_HIP",
            joint_c="RIGHT_HIP",
            min_angle_down=-5.0,  # Neutral
            max_angle_up=10.0,  # Target bend
            correct_range_min=10.0,  # Minimum bend
            # Hard safety limit (invalidates if exceeded)
            correct_range_max=25.0,
            max_deviation_deg=5.0,
            exercise_type='angle_based',
        ),

        # 9. Standing Arm Circles (Small)
        # Angle: Hip-Shoulder-OtherShoulder (tracks circular shoulder motion)
        # Correctness: Smooth, consistent angular velocity
        "Standing Arm Circles": ExerciseConfig(
            name="Standing Arm Circles",
            joint_a="LEFT_HIP",
            joint_b="LEFT_SHOULDER",
            joint_c="RIGHT_SHOULDER",
            min_angle_down=0.0,  # Starting position
            max_angle_up=60.0,  # Circular motion range
            correct_range_min=30.0,  # Minimum circular range
            correct_range_max=60.0,  # Maximum safe range
            max_deviation_deg=20.0,  # More forgiving for circular motion
            exercise_type='angle_based',
        ),

        # 10. Neutral Posture Hold
        # Metric: Shoulder-hip vertical alignment
        # Correct: Deviation <5° (uses displacement-based tracking)
        "Neutral Posture Hold": ExerciseConfig(
            name="Neutral Posture Hold",
            joint_a="LEFT_SHOULDER",  # Not used for angle, but required
            joint_b="LEFT_HIP",
            joint_c="RIGHT_HIP",
            min_angle_down=0.0,  # Not used
            max_angle_up=0.0,  # Not used
            correct_range_min=0.0,  # Not used
            correct_range_max=0.0,  # Not used
            exercise_type='displacement_based',
        ),
    }
