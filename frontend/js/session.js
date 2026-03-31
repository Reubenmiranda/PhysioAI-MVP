console.log("session.js loaded");
const API_BASE = API_CONFIG.baseUrl;


async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    credentials: "include",
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

function $(id) {
  return document.getElementById(id);
}

let pose = null;
let camera = null;
let lastUpdateTime = 0;
const UPDATE_INTERVAL_MS = 250; // throttle backend updates

// Audio feedback state
let lastTotalReps = 0;
let lastCorrectReps = 0;
let lastBeepTime = 0;
const BEEP_COOLDOWN_MS = 500;

const JOINT_INDICES = {
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
};

function showSessionMessage(text, type = "") {
  const el = $("session-message");
  el.textContent = text;
  el.className = `pa-message ${type}`;
}

function showCameraStatus(text, type = "") {
  const el = $("camera-status");
  el.textContent = text;
  el.className = `pa-message ${type}`;
}

// Track selected exercises and current index for button visibility
let selectedExercises = [];
try {
  const raw = sessionStorage.getItem("physioai_selected_exercises");
  if (raw) selectedExercises = JSON.parse(raw);
} catch (e) {}

function updateNextButtonVisibility(currentExerciseName) {
  const nextBtn = $("next-exercise-btn");
  if (!nextBtn) return;
  if (!currentExerciseName || selectedExercises.length === 0) {
    nextBtn.style.display = "none";
    return;
  }
  const idx = selectedExercises.indexOf(currentExerciseName);
  const isLast = idx === selectedExercises.length - 1;
  nextBtn.style.display = isLast ? "none" : "";
}

async function ensureActiveSession() {
  const { ok, status, data } = await apiGet("/session/status");
  if (!ok) {
    if (status === 401) {
      window.location.href = "index.html";
      return null;
    }
    showSessionMessage(data.error || "Failed to get session status.", "error");
    return null;
  }

  if (!data.has_active_session) {
    // No active session, redirect to exercise selection
    window.location.href = "exercises.html";
    return null;
  }

  $("current-exercise").textContent = data.current_exercise || "-";
  updateNextButtonVisibility(data.current_exercise);
  return data;
}

function onResults(results) {
  const now = performance.now();

  // Draw to canvas just for user visibility (optional)
  const videoEl = $("video");
  const canvasEl = $("output-canvas");
  const canvasCtx = canvasEl.getContext("2d");

  canvasEl.width = videoEl.videoWidth;
  canvasEl.height = videoEl.videoHeight;

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasEl.width, canvasEl.height);
  canvasCtx.drawImage(results.image, 0, 0, canvasEl.width, canvasEl.height);

  if (results.poseLandmarks) {
    // Draw skeleton using MediaPipe utilities (optional, simple)
    window.drawConnectors(
      canvasCtx,
      results.poseLandmarks,
      window.POSE_CONNECTIONS,
      { color: "#00FF00", lineWidth: 2 }
    );
    window.drawLandmarks(canvasCtx, results.poseLandmarks, {
      color: "#FF0000",
      lineWidth: 1,
      radius: 2,
    });
  }

  canvasCtx.restore();

  // Throttle backend updates
  if (!results.poseLandmarks || now - lastUpdateTime < UPDATE_INTERVAL_MS) {
    return;
  }
  lastUpdateTime = now;

  const lm = results.poseLandmarks;

  const getJoint = (idxKey) => {
    const idx = JOINT_INDICES[idxKey];
    const pt = lm[idx];
    if (!pt) return null;
    // x,y are already normalized 0-1 in MediaPipe
    return [Number(pt.x.toFixed(4)), Number(pt.y.toFixed(4))];
  };

  const landmarks = {
    LEFT_SHOULDER: getJoint("LEFT_SHOULDER"),
    RIGHT_SHOULDER: getJoint("RIGHT_SHOULDER"),
    LEFT_HIP: getJoint("LEFT_HIP"),
    RIGHT_HIP: getJoint("RIGHT_HIP"),
  };

  // Ensure all joints are present
  if (Object.values(landmarks).some((v) => v === null)) {
    showSessionMessage(
      "Unable to clearly see required joints. Please adjust your position.",
      "error"
    );
    return;
  }

  // Visibility (not available in all JS versions; use 1.0 as default if missing)
  const visibility = {};
  for (const [name, idx] of Object.entries(JOINT_INDICES)) {
    const pt = lm[idx];
    visibility[name] = pt.visibility !== undefined ? pt.visibility : 1.0;
  }

  sendUpdate(landmarks, visibility);
}

let sending = false;
async function sendUpdate(landmarks, visibility) {
  if (sending) return;
  sending = true;
  try {
    const { ok, status, data } = await apiPost("/session/update", {
      landmarks,
      visibility,
    });

    if (!ok) {
      if (status === 401) {
        window.location.href = "index.html";
        return;
      }
      showSessionMessage(data.error || "Update failed.", "error");
      return;
    }

    $("feedback-text").textContent = data.feedback || "";
    $("current-exercise").textContent = data.current_exercise || "-";
    updateNextButtonVisibility(data.current_exercise);

    if (data.metrics) {
      const correct = data.metrics.correct_reps ?? 0;
      const total = data.metrics.total_reps ?? 0;
      $("rep-correct").textContent = `${correct} / 10`;
      $("rep-total").textContent = `TOTAL: ${total}`;

      // Audio feedback logic
      const correctSound = document.getElementById("correctSound");
      const wrongSound = document.getElementById("wrongSound");

      if (total > lastTotalReps) {
        const now = Date.now();
        if (now - lastBeepTime > BEEP_COOLDOWN_MS) {
          if (correct > lastCorrectReps) {
            correctSound.currentTime = 0;
            correctSound.play().catch((err) => {
              // Ignore audio play errors (e.g., user interaction required)
              console.debug("Audio play failed:", err);
            });
          } else {
            wrongSound.currentTime = 0;
            wrongSound.play().catch((err) => {
              // Ignore audio play errors (e.g., user interaction required)
              console.debug("Audio play failed:", err);
            });
          }
          lastBeepTime = now;
        }
      }

      lastTotalReps = total;
      lastCorrectReps = correct;
    }

    if (!data.session_active) {
      showSessionMessage("Session completed. Ending session.", "success");
    }
  } finally {
    sending = false;
  }
}

async function initCameraAndPose() {
  const videoEl = $("video");
  const canvasEl = $("output-canvas");

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showCameraStatus("Webcam not supported in this browser.", "error");
    return;
  }

  showCameraStatus("Requesting camera access...");

  // Initialize MediaPipe Pose (classic JS API)
  pose = new window.Pose({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
  });

  pose.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    enableSegmentation: false,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  pose.onResults(onResults);

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: 640, height: 480 },
    audio: false,
  });

  videoEl.srcObject = stream;

  videoEl.addEventListener("loadeddata", () => {
    showCameraStatus("Camera active. Please position yourself in view.", "success");
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
  });

  camera = new window.Camera(videoEl, {
    onFrame: async () => {
      await pose.send({ image: videoEl });
    },
    width: 640,
    height: 480,
  });
  camera.start();
}

async function handleNextExercise() {
  const { ok, status, data } = await apiPost("/session/next", {});
  if (!ok) {
    if (status === 401) {
      window.location.href = "index.html";
      return;
    }
    showSessionMessage(data.error || "Failed to move to next exercise.", "error");
    return;
  }

  $("current-exercise").textContent = data.current_exercise || "-";
  updateNextButtonVisibility(data.current_exercise);
  showSessionMessage(data.message || "Moved to next exercise.", "success");
}

async function handleEndSession() {
  const { ok, status, data } = await apiPost("/session/end", {});
  if (!ok) {
    if (status === 401) {
      window.location.href = "index.html";
      return;
    }
    showSessionMessage(data.error || "Failed to end session.", "error");
    return;
  }

  // Save summary for summary page
  const breakdownRaw =
    data.exercise_breakdown ??
    data.exercises ??
    data.exercise_metrics ??
    [];

  const breakdownArray = Array.isArray(breakdownRaw)
    ? breakdownRaw
    : Object.entries(breakdownRaw || {}).map(([exercise_name, metrics]) => {
      const totalReps = metrics?.total_reps ?? 0;
      const correctReps = metrics?.correct_reps ?? 0;
      const incorrectReps =
        metrics?.incorrect_reps ?? Math.max(totalReps - correctReps, 0);

      return {
        exercise_name,
        total_reps: totalReps,
        correct_reps: correctReps,
        incorrect_reps: incorrectReps,
        posture_correctness_ratio: metrics?.posture_correctness_ratio ?? 0,
      };
    });

  const fallbackTotalReps = breakdownArray.reduce(
    (sum, item) => sum + (item.total_reps ?? 0),
    0
  );
  const fallbackTotalCorrect = breakdownArray.reduce(
    (sum, item) => sum + (item.correct_reps ?? 0),
    0
  );
  const fallbackTotalIncorrect = breakdownArray.reduce((sum, item) => {
    if (typeof item.incorrect_reps === "number") {
      return sum + item.incorrect_reps;
    }
    const total = item.total_reps ?? 0;
    const correct = item.correct_reps ?? 0;
    return sum + Math.max(total - correct, 0);
  }, 0);

  const overallScore = data.overall_score ?? data.session_score ?? 0;
  const payload = {
    overall_score: overallScore,
    session_score: overallScore,
    total_correct_reps:
      data.total_correct_reps ?? data.correct_reps ?? fallbackTotalCorrect,
    total_incorrect_reps:
      data.total_incorrect_reps ??
      data.incorrect_reps ??
      fallbackTotalIncorrect,
    total_reps: data.total_reps ?? fallbackTotalReps,
    exercise_breakdown: breakdownArray,
    exercises: breakdownArray,
    exercise_metrics: breakdownArray.reduce((acc, ex) => {
      acc[ex.exercise_name] = ex;
      return acc;
    }, {}),
  };
  sessionStorage.setItem("physioai_session_summary", JSON.stringify(payload));

  // Append to local session history (newest sessions should be visible in history page)
  try {
    const rawHistory = localStorage.getItem("physioai_session_history");
    let history = [];
    if (rawHistory) {
      try {
        const parsed = JSON.parse(rawHistory);
        if (Array.isArray(parsed)) {
          history = parsed;
        }
      } catch (e) {
        // Ignore malformed history and start fresh
        history = [];
      }
    }

    const now = new Date();
    const iso = now.toISOString();
    const exercisesList = Array.isArray(payload.exercises)
      ? Array.from(
          new Set(
            payload.exercises
              .map((ex) =>
                ex && ex.exercise_name != null ? String(ex.exercise_name) : ""
              )
              .filter((name) => name.trim().length > 0)
          )
        )
      : [];

    const historyEntry = {
      session_id: iso,
      date: iso,
      overall_score: overallScore,
      total_reps: payload.total_reps ?? 0,
      exercises: exercisesList,
      per_exercise_metrics: payload.exercise_metrics || null,
    };

    history.push(historyEntry);
    localStorage.setItem("physioai_session_history", JSON.stringify(history));
  } catch (e) {
    console.error("Failed to append session history:", e);
  }

  // Redirect to summary
  window.location.href = "summary.html";
}

document.addEventListener("DOMContentLoaded", async () => {
  const status = await ensureActiveSession();
  if (!status) return;

  $("next-exercise-btn").addEventListener("click", handleNextExercise);
  $("end-session-btn").addEventListener("click", handleEndSession);

  initCameraAndPose().catch((err) => {
    console.error(err);
    showCameraStatus("Failed to start camera. Check permissions and try again.", "error");
  });
});

