# PhysioAI - Phase Handoff Document
## Core System → Frontend Development

**Status**: ✅ **Core System Stable & Locked**  
**Date**: Handoff to Frontend Phase  
**Purpose**: Internal documentation for frontend integration

---

## 1️⃣ System Architecture (As-Is)

### Core Modules and Responsibilities

#### **`utils/pose_module.py`** - Pose Detection Layer
- **Purpose**: Webcam capture and MediaPipe Pose integration
- **Key Class**: `PoseDetector`
- **Responsibilities**:
  - Initialize webcam (OpenCV VideoCapture)
  - Process frames through MediaPipe Pose
  - Extract joint landmarks (4 joints only)
  - Return normalized coordinates (0-1) with visibility scores
  - Draw pose skeleton overlay on video frames
- **API Compatibility**: Supports MediaPipe 0.9.x and 2.x (0.10.x+)
- **Output**: `PoseResult` dataclass containing:
  - `image_bgr`: OpenCV BGR image with pose overlay
  - `landmarks`: `Dict[str, Tuple[float, float]]` (normalized x, y coordinates)
  - `visibility`: `Dict[str, float]` (0.0-1.0 visibility scores)
  - `pose_detected`: `bool` (all 4 joints visible with visibility > 0.6)

#### **`utils/exercise_logic.py`** - Exercise Detection & Rep Counting
- **Purpose**: Exercise configuration, angle calculation, and rep counting logic
- **Key Classes**: `ExerciseConfig`, `ExerciseState`, `ExerciseMetrics`
- **Key Functions**:
  - `calculate_angle(a, b, c)`: Three-point angle calculation using cosine rule
  - `calculate_vertical_displacement(p1, p2)`: Vertical displacement between two points
  - `calculate_angle_to_horizontal(p1, p2)`: Angle between line and horizontal axis
  - `default_exercise_configs()`: Returns dict of 10 fixed exercise configurations
- **Responsibilities**:
  - Manage exercise configurations (angle thresholds, joint mappings)
  - Calculate joint angles from landmarks
  - Track neutral reference angle at exercise start
  - Implement rep counting state machine (neutral → active → neutral)
  - Classify reps as correct/incorrect based on safety thresholds
  - Track posture correctness duration for scoring
  - Generate real-time feedback text

#### **`utils/session_manager.py`** - Session Lifecycle Management
- **Purpose**: Orchestrate multi-exercise sessions and aggregate metrics
- **Key Classes**: `SessionManager`, `SessionMetrics`
- **Responsibilities**:
  - Hold catalog of 10 exercises
  - Validate exactly 5 exercises selected per session
  - Run exercises sequentially (one at a time)
  - Update current exercise with pose landmarks
  - Auto-advance when exercise reaches 10 correct reps
  - Aggregate per-exercise metrics
  - Compute final session score (0-100)
  - Track session active/inactive state

#### **`main.py`** - Entry Point (Console Prototype)
- **Purpose**: Demonstrates full session flow using console UI
- **Responsibilities**:
  - Initialize `PoseDetector` and `SessionManager`
  - Auto-select first 5 exercises (placeholder for frontend selection)
  - Main loop: read webcam → detect pose → update exercise → display feedback
  - Handle keyboard input ('n' for next, 'q' for quit)
  - Display session summary on completion
- **Note**: This is a **prototype** that will be replaced by Flask backend + web frontend

### Data Flow Pipeline

```
Webcam (OpenCV)
    ↓
PoseDetector.read()
    ↓
MediaPipe Pose Detection
    ↓
Extract 4 Joints (Shoulders + Hips)
    ↓
SessionManager.update_with_landmarks(landmarks)
    ↓
ExerciseState.update(landmarks)
    ↓
Calculate Angles / Displacement
    ↓
Rep Counting State Machine
    ↓
ExerciseMetrics (reps, correctness, posture duration)
    ↓
SessionMetrics (aggregated across 5 exercises)
    ↓
Session Score (0-100)
```

---

## 2️⃣ Exercise System (Locked)

### Final List of 10 Exercises

The system supports exactly **10 fixed exercises**. These are defined in `default_exercise_configs()` and **MUST NOT** be changed:

1. **Standing Hip Flexion** (`angle_based`)
   - Joints: LEFT_SHOULDER, LEFT_HIP, RIGHT_HIP
   - Detects forward lean (hip flexion)

2. **Glute Bridge** (`glute_bridge` - special type)
   - Joints: LEFT_SHOULDER, LEFT_HIP (uses shoulder-hip line to horizontal)
   - Side-view camera required
   - Neutral: 40°-60° (supine), Bridge: 15°-35° (hip elevated)

3. **Cobra Pose** (`cobra_pose` - special type)
   - Joints: LEFT_SHOULDER, LEFT_HIP (uses shoulder-hip line to horizontal)
   - Prone back extension, side-view camera
   - Neutral: 5°-15°, Target: 25°-45°, Safety: >50° invalid

4. **Standing March** (`angle_based`)
   - Joints: LEFT_SHOULDER, LEFT_HIP, RIGHT_HIP
   - Low knee lift movement

5. **Standing Forward Arm Raise** (`angle_based`)
   - Joints: LEFT_HIP, LEFT_SHOULDER, RIGHT_SHOULDER
   - Shoulder flexion forward

6. **Standing Lateral Arm Raise** (`angle_based`)
   - Joints: LEFT_HIP, LEFT_SHOULDER, RIGHT_SHOULDER
   - Shoulder abduction (side raise)

7. **Shoulder Shrugs** (`displacement_based`)
   - Tracks vertical displacement of shoulders relative to hips
   - No angle calculation

8. **Standing Trunk Side Bend** (`angle_based`)
   - Joints: LEFT_SHOULDER, LEFT_HIP, RIGHT_HIP
   - Lateral trunk deviation
   - Hard safety limit: >25° invalid

9. **Standing Arm Circles** (`angle_based`)
   - Joints: LEFT_HIP, LEFT_SHOULDER, RIGHT_SHOULDER
   - Circular shoulder motion tracking

10. **Neutral Posture Hold** (`displacement_based`)
    - Tracks shoulder-hip vertical alignment
    - Correct if deviation < 5% (approximately 5 degrees)

### Detection Approaches

#### **Angle-Based Detection** (8 exercises)
- Uses three-point angle calculation: `calculate_angle(joint_a, joint_b, joint_c)`
- Captures neutral reference angle over first 30 frames (median-based)
- Computes deviation from neutral for rep counting
- State machine: `neutral → down position → up position → neutral` (counts rep)

#### **Displacement-Based Detection** (2 exercises)
- **Shoulder Shrugs**: Vertical displacement of shoulders relative to hips
- **Neutral Posture Hold**: Vertical alignment deviation between shoulders and hips
- Uses `calculate_vertical_displacement()` or alignment calculations
- Different rep counting logic tailored to each exercise

#### **Special Angle Calculations** (2 exercises)
- **Glute Bridge**: Uses `calculate_angle_to_horizontal()` (shoulder-hip line to horizontal)
- **Cobra Pose**: Uses `calculate_angle_to_horizontal()` (shoulder-hip line to horizontal)
- These use absolute angles (not deviation from neutral) due to side-view camera perspective

### Rep Counting Method

#### **State Machine: Neutral → Active → Neutral**

All exercises use a state machine approach with these states:

1. **Neutral Position**:
   - Angle/displacement within neutral range
   - Ready to start next repetition

2. **Active Position** (down/up):
   - User moves into active range
   - System tracks peak angle/displacement during movement
   - Monitors safety bounds (prevents excessive depth/extension)

3. **Return to Neutral**:
   - User returns to neutral position
   - Triggers rep counting evaluation
   - Classifies as correct/incorrect based on peak position

#### **Rep Classification**

A rep is counted as **correct** if:
- Peak angle/displacement is within `correct_range_min` to `correct_range_max`
- Does not exceed safety bounds (`max_deviation_deg`, `correct_range_max`)
- Exercise-specific safety checks pass (e.g., Cobra Pose: angle ≤ 50°)

A rep is counted as **incorrect** if:
- Peak position outside correct range
- Safety threshold exceeded
- Movement too shallow or too deep

#### **Neutral Reference Capture**

- Captures neutral reference over first 30 frames at exercise start
- Uses median of samples for robustness against outliers
- All angle-based calculations use **deviation from neutral** (except Glute Bridge and Cobra Pose which use absolute angles)

### Safety Philosophy

#### **Conservative Thresholds**
- All exercises have safety bounds (`correct_range_max`) that invalidate excessive movements
- Examples:
  - Standing Trunk Side Bend: Hard limit at 25° (>25° = unsafe)
  - Cobra Pose: >50° = overextension (invalid)
  - Glute Bridge: <10° = excessive arching (safety warning)

#### **Under-Counting Preferred**
- System is intentionally conservative
- Prefers missing a rep over counting an unsafe movement
- Safety checks stop counting if unsafe position detected
- Real-time feedback warns user of unsafe positions

#### **Non-Diagnostic Language**
- All feedback text uses non-medical, safety-focused language
- Examples: "Reduce elevation for safety", "If you feel discomfort, stop immediately"
- No medical diagnosis or treatment recommendations

---

## 3️⃣ Pose Detection & Joints

### MediaPipe Pose Usage

- **Model**: MediaPipe PoseLandmarker Lite (`pose_landmarker_lite.task`)
- **Auto-Download**: Model downloads automatically on first run (~3MB)
- **Compatibility**: Supports MediaPipe 0.9.x and 2.x (0.10.x+) APIs
- **Confidence Thresholds**:
  - `min_detection_confidence`: 0.5 (default)
  - `min_tracking_confidence`: 0.5 (default)

### Tracked Joints (Locked to 4 Joints Only)

The system tracks **ONLY** these 4 joints. **DO NOT** add more joints:

- **LEFT_SHOULDER** (MediaPipe index: 11 / LEFT_SHOULDER)
- **RIGHT_SHOULDER** (MediaPipe index: 12 / RIGHT_SHOULDER)
- **LEFT_HIP** (MediaPipe index: 23 / LEFT_HIP)
- **RIGHT_HIP** (MediaPipe index: 24 / RIGHT_HIP)

**Rationale**: All 10 exercises are designed to work with shoulder and hip joints only. Adding knees, elbows, or other joints would require rewriting all exercise logic.

### Camera Assumptions

- **Side View for Bed Exercises**:
  - Glute Bridge and Cobra Pose assume side-view camera angle
  - Shoulder-hip line to horizontal calculation only works with side view
  - User should lie on bed/mat with camera positioned to side

- **Stable Webcam Feed**:
  - Assumes stable camera position (not moving during session)
  - Neutral reference capture depends on stable camera
  - Works best with mounted/stationary webcam

- **Lighting & Visibility**:
  - Requires good lighting for MediaPipe to detect joints
  - All 4 joints must be visible (visibility > 0.6) for pose detection
  - System provides feedback if joints not clearly visible

---

## 4️⃣ Session Management

### Session Configuration

- **Exactly 5 Exercises**: Each session requires exactly 5 exercises selected from the catalog of 10
- **Validation**: `SessionManager.configure_session()` enforces this requirement
- **Error Handling**: Raises `ValueError` if:
  - Number of exercises ≠ 5
  - Unknown exercise name provided

### Sequential Exercise Execution

- Exercises run **one at a time** (sequential, not parallel)
- Current exercise tracked by `current_index` (0-4)
- User completes one exercise before moving to next
- Manual advance: `SessionManager.next_exercise()`
- Auto-advance: System automatically calls `next_exercise()` when `correct_reps >= 10`

### Metrics Captured

#### **Per-Exercise Metrics** (`ExerciseMetrics`):
- `exercise_name`: str
- `total_reps`: int (all counted reps, correct + incorrect)
- `correct_reps`: int (reps within correct range, capped at 10 for scoring)
- `incorrect_reps`: int (reps outside correct range or unsafe)
- `angle_sum`: float (accumulated angle values for statistics)
- `angle_count`: int (number of angle measurements)
- `correct_posture_frames`: int (frames spent in correct posture range)
- `total_frames`: int (total frames processed for exercise)

**Computed Properties**:
- `average_angle`: float (angle_sum / angle_count)
- `average_angle_deviation`: float (deviation from ideal)
- `posture_correctness_ratio`: float (correct_posture_frames / total_frames, 0.0-1.0)

#### **Session-Level Metrics** (`SessionMetrics`):
- `exercises`: `Dict[str, ExerciseMetrics]` (one entry per exercise in session)
- `session_score`: float (0.0-100.0, computed on session end)

### Final Session Score (0-100)

**Formula**: Weighted combination of rep-based score (60%) and posture correctness (40%)

1. **Rep-Based Score (60% weight)**:
   - Per exercise: `capped_correct_reps / max(total_reps, 10)` × 100
   - `capped_correct_reps = min(correct_reps, 10)` (caps at 10 per exercise)
   - Average across all 5 exercises

2. **Posture Correctness Score (40% weight)**:
   - Per exercise: `posture_correctness_ratio × 100`
   - Average across all 5 exercises

3. **Final Score**:
   ```
   session_score = (0.6 × avg_reps_score) + (0.4 × avg_posture_score)
   ```
   - Normalized to 0.0-100.0 range

**Scoring Philosophy**:
- Rewards correct repetitions (60% weight)
- Also rewards maintaining correct posture throughout exercise (40% weight)
- Each exercise contributes equally to final score
- Maximum possible score per exercise: 10 points (10 correct reps)

---

## 5️⃣ Stable Interfaces for Frontend

### SessionManager API

#### **`configure_session(selected_exercises: List[str]) -> None`**
- **Purpose**: Initialize a new session with 5 selected exercises
- **Input**: List of exactly 5 exercise names (must match keys from `default_exercise_configs()`)
- **Side Effects**:
  - Sets `session_active = True`
  - Initializes `exercise_states` dict for each selected exercise
  - Resets `current_index = 0`
  - Clears previous `metrics`
- **Raises**: `ValueError` if validation fails

#### **`update_with_landmarks(landmarks: Dict[str, Tuple[float, float]]) -> str`**
- **Purpose**: Update current exercise with latest pose landmarks from webcam
- **Input**: Dictionary mapping joint names to normalized (x, y) coordinates
  - Expected keys: `"LEFT_SHOULDER"`, `"RIGHT_SHOULDER"`, `"LEFT_HIP"`, `"RIGHT_HIP"`
- **Returns**: Feedback text string (e.g., "Exercise: Good repetition. Keep breathing.")
- **Side Effects**:
  - Updates current exercise's `ExerciseState`
  - Stores latest `ExerciseMetrics` in `session.metrics.exercises`
  - Auto-advances to next exercise if `correct_reps >= 10`
  - Increments frame counters and posture correctness tracking
- **Usage**: Call this once per webcam frame when landmarks are available

#### **`next_exercise() -> None`**
- **Purpose**: Manually advance to next exercise in sequence
- **Side Effects**:
  - Increments `current_index`
  - If `current_index >= len(selected_exercises)`, calls `end_session()` automatically
- **Usage**: Call when user clicks "Next Exercise" button, or when auto-advance triggers

#### **`end_session() -> None`**
- **Purpose**: Mark session as finished and compute final score
- **Side Effects**:
  - Sets `session_active = False`
  - Computes `session.metrics.session_score` using `_compute_session_score()`
- **Usage**: Call when user clicks "End Session" button, or when all exercises completed

#### **`get_current_exercise_name() -> str`**
- **Purpose**: Get name of currently active exercise
- **Returns**: Exercise name string, or empty string if session inactive
- **Usage**: Display current exercise name in UI

### Data Structures Returned

#### **ExerciseMetrics** (Access via `session.metrics.exercises[exercise_name]`):
```python
@dataclass
class ExerciseMetrics:
    exercise_name: str
    total_reps: int
    correct_reps: int
    incorrect_reps: int
    angle_sum: float
    angle_count: int
    correct_posture_frames: int
    total_frames: int
    
    # Properties (computed on access):
    average_angle: float
    average_angle_deviation: float
    posture_correctness_ratio: float  # 0.0-1.0
```

#### **SessionMetrics** (Access via `session.metrics`):
```python
@dataclass
class SessionMetrics:
    exercises: Dict[str, ExerciseMetrics]  # One entry per exercise
    session_score: float  # 0.0-100.0, computed on end_session()
```

### Feedback Text

The `update_with_landmarks()` method returns a feedback string that provides:
- Exercise name
- Current status ("Good repetition", "Establishing baseline", etc.)
- Safety warnings if unsafe position detected
- Posture guidance ("Keep it controlled", "Return to neutral slowly", etc.)

**Example Feedback Strings**:
- `"Standing Hip Flexion: Establishing baseline. Stand in neutral position."`
- `"Glute Bridge: Good bridge position. Hold briefly, then lower slowly."`
- `"Cobra Pose: Avoid overextending your back. Ease down slowly."`

### PoseDetector API (For Backend Integration)

#### **`PoseDetector.__init__(camera_index: int = 0, ...)`**
- **Purpose**: Initialize webcam and MediaPipe Pose
- **Parameters**: `camera_index` (default: 0), confidence thresholds

#### **`read() -> Optional[PoseResult]`**
- **Purpose**: Capture frame from webcam and run pose detection
- **Returns**: `PoseResult` if frame captured, `None` if webcam unavailable
- **Usage**: Call in a loop (typically 30 FPS) to get continuous pose updates

#### **`release() -> None`**
- **Purpose**: Release webcam and MediaPipe resources
- **Usage**: Call when session ends to free camera

#### **PoseResult Structure**:
```python
@dataclass
class PoseResult:
    image_bgr: np.ndarray  # OpenCV BGR image (can be encoded to JPEG for web)
    landmarks: Optional[Dict[str, Tuple[float, float]]]  # Normalized coordinates
    visibility: Optional[Dict[str, float]]  # Visibility scores
    pose_detected: bool  # True if all 4 joints visible
```

---

## 6️⃣ What Is Explicitly Locked (Do Not Change)

### ❌ Exercise Definitions
- **DO NOT** modify `default_exercise_configs()` in `exercise_logic.py`
- **DO NOT** change exercise names, joint mappings, or angle thresholds
- **DO NOT** add new exercises or remove existing ones
- **Rationale**: All 10 exercises are finalized and tested. Changes would break rep counting logic.

### ❌ Joint Set (Shoulder + Hip Only)
- **DO NOT** add new joints (knees, elbows, wrists, etc.)
- **DO NOT** modify `JOINTS` dict in `PoseDetector` class
- **Rationale**: All exercise logic assumes 4 joints only. Adding joints requires complete rewrite.

### ❌ Angle Logic & Thresholds
- **DO NOT** modify `calculate_angle()`, `calculate_vertical_displacement()`, or `calculate_angle_to_horizontal()`
- **DO NOT** change angle threshold values in `ExerciseConfig` (e.g., `correct_range_min`, `correct_range_max`)
- **DO NOT** modify `max_deviation_deg` or `safety_margin_deg` values
- **Rationale**: Thresholds are calibrated for safety and correctness. Changes could make system unsafe or inaccurate.

### ❌ Rep Counting State Machine
- **DO NOT** modify the rep counting logic in `ExerciseState.update()`
- **DO NOT** change state transitions (neutral → down → up → neutral)
- **DO NOT** modify neutral reference capture logic (30 frames, median-based)
- **Rationale**: Rep counting is stable and tested. Changes would break correctness classification.

### ❌ Scoring Formula
- **DO NOT** modify `SessionManager._compute_session_score()`
- **DO NOT** change the 60% reps / 40% posture weight ratio
- **DO NOT** modify the per-exercise score capping (10 correct reps max)
- **Rationale**: Scoring formula is finalized and consistent. Changes would affect historical score comparisons.

### ❌ Safety Constraints
- **DO NOT** relax safety thresholds (e.g., increase `correct_range_max` beyond safe limits)
- **DO NOT** remove safety checks (e.g., Cobra Pose >50° check, Glute Bridge <10° check)
- **DO NOT** modify safety warning feedback text
- **Rationale**: Safety constraints protect users from injury. Relaxing them would be unsafe.

### ❌ Core Module Interfaces
- **DO NOT** change function signatures of `SessionManager` methods
- **DO NOT** modify `ExerciseMetrics` or `SessionMetrics` dataclass structures
- **DO NOT** change return types or parameter types
- **Rationale**: Frontend will depend on these interfaces. Changes would break integration.

### ✅ What CAN Be Changed (Safe Modifications)

- **Frontend UI/UX**: HTML, CSS, JavaScript (any changes)
- **Backend Routes**: Flask routes, API endpoints (as long as they call locked interfaces correctly)
- **Database Schema**: Can add new tables/fields for user management, session history, etc.
- **Visual Feedback**: Can modify how feedback text is displayed (fonts, colors, animations)
- **Webcam Display**: Can change how video feed is rendered (size, overlay styling, etc.)
- **Error Messages**: Can improve error handling in Flask layer (but keep core validation in SessionManager)

---

## 7️⃣ What Comes Next (Frontend Phase)

### Web UI Goals

#### **1. Exercise Selection Page**
- Display list of all 10 exercises with checkboxes
- Enforce exactly 5 selections (disable submit until 5 selected)
- Allow user to see exercise descriptions/instructions
- Submit selected exercises to backend to start session

#### **2. Live Session Page**
- **Webcam Feed Display**:
  - Show real-time video from user's webcam
  - Overlay pose skeleton (optional, can use MediaPipe's visualization or custom)
  - Display tracking status ("Pose Detected" / "Tracking Lost")
  
- **Exercise Information Panel**:
  - Current exercise name
  - Target: "10 correct reps"
  - Progress indicator (e.g., "7/10 correct reps")
  
- **Real-Time Feedback**:
  - Display feedback text from `SessionManager.update_with_landmarks()`
  - Color-coded feedback (green for good, yellow for warning, red for unsafe)
  - Optional: Visual indicators (angles, joint positions) if desired
  
- **Controls**:
  - "Next Exercise" button (calls `SessionManager.next_exercise()`)
  - "End Session" button (calls `SessionManager.end_session()`)
  - Auto-advance indicator (when 10 correct reps reached)

#### **3. Session Summary Page**
- Display session metrics:
  - Per-exercise breakdown:
    - Exercise name
    - Correct reps / Total reps
    - Score (capped at 10)
    - Average angle deviation
    - Posture correctness percentage
  - Overall session score (0-100)
- Generate AI report (optional, if OpenAI integration added)
- Option to save session to history

#### **4. Session History & Reports Page**
- List of past sessions (date, score, exercises completed)
- Click to view detailed session report
- Option to export report as PDF (future enhancement)

### Technical Implementation Suggestions

#### **Backend (Flask) Routes Needed**:
```python
POST /api/session/start
    - Input: {"exercises": ["Exercise1", "Exercise2", ...]}  # Exactly 5
    - Returns: {"session_id": "...", "status": "active"}

POST /api/session/update
    - Input: {"landmarks": {"LEFT_SHOULDER": [x, y], ...}}
    - Returns: {"feedback": "...", "metrics": {...}, "current_exercise": "..."}

POST /api/session/next
    - Advances to next exercise
    - Returns: {"current_exercise": "..."}

POST /api/session/end
    - Ends session, computes score
    - Returns: {"metrics": {...}, "session_score": 100.0}

GET /api/webcam/stream
    - Returns: JPEG frames from webcam (optional, if not using client-side MediaPipe)
```

#### **Frontend Technologies**:
- **HTML5 + CSS3 + JavaScript** (vanilla or framework like React/Vue)
- **WebRTC** or **MediaRecorder API** for webcam access
- **WebSockets** (optional) for real-time updates if using server-side pose detection
- **Chart.js** or **D3.js** for visualizing session metrics

#### **Key Integration Points**:
1. **Webcam Access**: Use `navigator.mediaDevices.getUserMedia()` to access webcam
2. **MediaPipe in Browser** (optional): Use MediaPipe Pose JavaScript API for client-side detection, or stream frames to backend
3. **API Calls**: Frontend calls Flask routes, which internally call `SessionManager` methods
4. **State Management**: Frontend tracks current session state (active exercise, progress, etc.)

### Expected User Flow

1. **Login** (if user management added)
2. **Select 5 Exercises** → Submit
3. **Live Session**:
   - Webcam starts
   - System detects pose
   - User performs exercises
   - Real-time feedback displayed
   - Auto-advance or manual "Next" button
4. **Session Summary** → View metrics and score
5. **Save to History** (optional)
6. **View History** → Access past sessions

---

## 📋 Summary Checklist for Frontend Developer

- [ ] Understand `SessionManager` API: `configure_session()`, `update_with_landmarks()`, `next_exercise()`, `end_session()`
- [ ] Understand data structures: `ExerciseMetrics`, `SessionMetrics`, `PoseResult`
- [ ] Know the 10 exercises by name (for exercise selection UI)
- [ ] Know that exactly 5 exercises must be selected per session
- [ ] Understand scoring: 10 correct reps per exercise (max), session score 0-100 (60% reps, 40% posture)
- [ ] Know that rep counting uses state machine (neutral → active → neutral)
- [ ] Know that system auto-advances when `correct_reps >= 10`
- [ ] Understand feedback text format (returned by `update_with_landmarks()`)
- [ ] Know that 4 joints only: LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP
- [ ] Know camera assumptions: side-view for Glute Bridge/Cobra Pose, stable webcam for others
- [ ] **DO NOT** modify core modules: `exercise_logic.py`, `session_manager.py`, `pose_module.py`
- [ ] **DO NOT** change exercise definitions, joint set, thresholds, rep counting, or scoring

---

## 🎯 Integration Example (Pseudo-Code)

```python
# Flask Backend (app.py)
from utils.session_manager import SessionManager
from utils.pose_module import PoseDetector

session_manager = SessionManager()

@app.route('/api/session/start', methods=['POST'])
def start_session():
    exercises = request.json['exercises']  # List of 5 exercise names
    session_manager.configure_session(exercises)
    return {"status": "active", "current_exercise": session_manager.get_current_exercise_name()}

@app.route('/api/session/update', methods=['POST'])
def update_session():
    landmarks = request.json['landmarks']  # Dict with 4 joints
    feedback = session_manager.update_with_landmarks(landmarks)
    current_exercise = session_manager.get_current_exercise_name()
    metrics = session_manager.metrics.exercises.get(current_exercise)
    
    return {
        "feedback": feedback,
        "current_exercise": current_exercise,
        "metrics": {
            "total_reps": metrics.total_reps,
            "correct_reps": metrics.correct_reps,
            "score": min(metrics.correct_reps, 10)
        },
        "session_active": session_manager.session_active
    }

@app.route('/api/session/end', methods=['POST'])
def end_session():
    session_manager.end_session()
    return {
        "session_score": session_manager.metrics.session_score,
        "exercises": {name: {
            "correct_reps": m.correct_reps,
            "total_reps": m.total_reps,
            "posture_ratio": m.posture_correctness_ratio
        } for name, m in session_manager.metrics.exercises.items()}
    }
```

```javascript
// Frontend (session.js)
async function updateSession(landmarks) {
    const response = await fetch('/api/session/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({landmarks: landmarks})
    });
    const data = await response.json();
    
    // Update UI with feedback and metrics
    document.getElementById('feedback').textContent = data.feedback;
    document.getElementById('score').textContent = `${data.metrics.score}/10`;
    
    if (!data.session_active) {
        // Auto-advance to next exercise or end session
        window.location.href = '/session/summary';
    }
}
```

---

**Status**: ✅ **Ready for Frontend Development**  
**Next Phase**: Web UI Implementation + Flask Backend Integration
