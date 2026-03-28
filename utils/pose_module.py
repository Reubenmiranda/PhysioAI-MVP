import cv2
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import os
import urllib.request

import mediapipe as mp

# ---------------------------------------------------------------------------
# MediaPipe 2.x API (for MediaPipe 0.10.x+)
# ---------------------------------------------------------------------------
# MediaPipe 2.x uses PoseLandmarker which requires a model file
# This module automatically downloads the model if needed

try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    USE_NEW_API = True
except ImportError:
    USE_NEW_API = False
    try:
        # Fallback to MediaPipe 0.9.x API
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
    except AttributeError:
        raise ImportError(
            "MediaPipe is not properly installed. "
            "Please install: pip install mediapipe"
        )


# Model URL for MediaPipe 2.x PoseLandmarker
POSE_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/"
    "pose_landmarker_lite.task"
)
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "pose_landmarker_lite.task")


def _download_model():
    """Download the MediaPipe PoseLandmarker model if it doesn't exist."""
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Downloading MediaPipe PoseLandmarker model to {MODEL_PATH}...")
    print("This is a one-time download (~3MB).")
    
    try:
        urllib.request.urlretrieve(POSE_LANDMARKER_MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully!")
        return MODEL_PATH
    except Exception as e:
        raise RuntimeError(
            f"Failed to download MediaPipe model: {e}\n"
            f"Please manually download from: {POSE_LANDMARKER_MODEL_URL}\n"
            f"and save to: {MODEL_PATH}"
        )


@dataclass
class PoseResult:
    """Lightweight container for pose detection outputs."""

    image_bgr: any
    landmarks: Optional[Dict[str, Tuple[float, float]]]
    visibility: Optional[Dict[str, float]]
    pose_detected: bool


class PoseDetector:
    """
    Wrapper around MediaPipe Pose.

    Supports both MediaPipe 0.9.x (mp.solutions.pose) and MediaPipe 2.x (PoseLandmarker).
    Automatically detects which version is installed and uses the appropriate API.
    """

    # Landmark indices for required joints
    if USE_NEW_API:
        # MediaPipe 2.x uses integer indices
        JOINTS = {
            'LEFT_SHOULDER': 11,
            'RIGHT_SHOULDER': 12,
            'LEFT_HIP': 23,
            'RIGHT_HIP': 24,
        }
    else:
        JOINTS = {
            'LEFT_SHOULDER': mp_pose.PoseLandmark.LEFT_SHOULDER,
            'RIGHT_SHOULDER': mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'LEFT_HIP': mp_pose.PoseLandmark.LEFT_HIP,
            'RIGHT_HIP': mp_pose.PoseLandmark.RIGHT_HIP,
        }

    def __init__(
        self,
        camera_index: int = 0,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.cap = cv2.VideoCapture(camera_index)
        self.USE_NEW_API = USE_NEW_API
        self.frame_timestamp_ms = 0
        
        if USE_NEW_API:
            # MediaPipe 2.x API
            model_path = _download_model()
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                min_pose_detection_confidence=min_detection_confidence,
                min_pose_presence_confidence=min_tracking_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
            self.pose_landmarker = vision.PoseLandmarker.create_from_options(options)
        else:
            # MediaPipe 0.9.x API
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )

    def _process_frame_mp2(self, frame):
        """Process frame using MediaPipe 2.x API."""
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        detection_result = self.pose_landmarker.detect_for_video(
            mp_image, self.frame_timestamp_ms
        )
        
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        landmarks_dict: Dict[str, Tuple[float, float]] = {}
        visibility_dict: Dict[str, float] = {}
        pose_detected = False

        if detection_result.pose_landmarks and len(detection_result.pose_landmarks) > 0:
            pose_landmarks = detection_result.pose_landmarks[0]
            self._draw_landmarks_mp2(image_bgr, pose_landmarks)

            visible_flags = []
            for joint_name, joint_idx in self.JOINTS.items():
                if joint_idx < len(pose_landmarks):
                    landmark = pose_landmarks[joint_idx]
                    x = round(landmark.x, 4)
                    y = round(landmark.y, 4)
                    landmarks_dict[joint_name] = (x, y)
                    # MediaPipe 2.x visibility is typically 1.0 if landmark exists
                    visibility_dict[joint_name] = getattr(landmark, 'visibility', 1.0)
                    visible_flags.append(visibility_dict[joint_name] > 0.6)

            pose_detected = all(visible_flags) if visible_flags else False

        return PoseResult(
            image_bgr=image_bgr,
            landmarks=landmarks_dict if landmarks_dict else None,
            visibility=visibility_dict if visibility_dict else None,
            pose_detected=pose_detected,
        )

    def _draw_landmarks_mp2(self, image_bgr, landmarks):
        """Draw pose landmarks using MediaPipe 2.x structure."""
        h, w = image_bgr.shape[:2]
        connections = [
            (11, 12),  # Left shoulder to right shoulder
            (11, 23),  # Left shoulder to left hip
            (12, 24),  # Right shoulder to right hip
            (23, 24),  # Left hip to right hip
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                pt1 = (int(start.x * w), int(start.y * h))
                pt2 = (int(end.x * w), int(end.y * h))
                cv2.line(image_bgr, pt1, pt2, (0, 255, 0), 2)
        
        for joint_name, joint_idx in self.JOINTS.items():
            if joint_idx < len(landmarks):
                landmark = landmarks[joint_idx]
                pt = (int(landmark.x * w), int(landmark.y * h))
                cv2.circle(image_bgr, pt, 5, (0, 0, 255), -1)

    def _process_frame_mp09(self, frame):
        """Process frame using MediaPipe 0.9.x API."""
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        landmarks_dict: Dict[str, Tuple[float, float]] = {}
        visibility_dict: Dict[str, float] = {}
        pose_detected = False

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

            landmarks = results.pose_landmarks.landmark
            visible_flags = []

            for joint_name, joint_idx in self.JOINTS.items():
                joint = landmarks[joint_idx.value]
                x = round(joint.x, 4)
                y = round(joint.y, 4)
                landmarks_dict[joint_name] = (x, y)
                visibility_dict[joint_name] = joint.visibility
                visible_flags.append(joint.visibility > 0.6)

            pose_detected = all(visible_flags) if visible_flags else False

        return PoseResult(
            image_bgr=image_bgr,
            landmarks=landmarks_dict if landmarks_dict else None,
            visibility=visibility_dict if visibility_dict else None,
            pose_detected=pose_detected,
        )

    def _process_frame(self, frame):
        """Run MediaPipe on a single frame and extract selected joints."""
        if self.USE_NEW_API:
            return self._process_frame_mp2(frame)
        else:
            return self._process_frame_mp09(frame)

    def read(self) -> Optional[PoseResult]:
        """
        Capture a frame from the webcam and run pose detection.

        Returns:
            PoseResult if a frame was captured, otherwise None.
        """
        if not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Increment timestamp for MediaPipe 2.x video mode
        if self.USE_NEW_API:
            self.frame_timestamp_ms += 33  # ~30 FPS
        
        return self._process_frame(frame)

    def release(self) -> None:
        """Release webcam and MediaPipe resources."""
        if self.cap.isOpened():
            self.cap.release()
        if self.USE_NEW_API:
            self.pose_landmarker.close()
        else:
            self.pose.close()


def overlay_tracking_status(image_bgr, pose_detected: bool) -> None:
    """
    Draw simple tracking feedback on the frame.

    Separated into a helper to keep UI logic out of the main application.
    """
    if pose_detected:
        text = "Pose Detected"
        color = (0, 255, 0)
    else:
        text = "Tracking Lost"
        color = (0, 0, 255)

    cv2.putText(
        image_bgr,
        text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3,
        cv2.LINE_AA,
    )
