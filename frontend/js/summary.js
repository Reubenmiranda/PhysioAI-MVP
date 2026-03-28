/**
 * Fixed list of supported exercises (matches backend default_exercise_configs)
 */
const ALL_EXERCISES = [
  "Standing Hip Flexion",
  "Glute Bridge",
  "Cobra Pose",
  "Standing March",
  "Standing Forward Arm Raise",
  "Standing Lateral Arm Raise",
  "Shoulder Shrugs",
  "Standing Trunk Side Bend",
  "Standing Arm Circles",
  "Neutral Posture Hold",
];

function defaultMetrics() {
  return {
    correct_reps: 0,
    incorrect_reps: 0,
    total_reps: 0,
    posture_correctness_ratio: 0,
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const scoreEl = document.getElementById("overall-score");
  const totalEl = document.getElementById("total-reps");
  const tableBody = document.querySelector("#summary-table tbody");
  const msgEl = document.getElementById("summary-message");

  function setText(el, text) {
    if (el) el.textContent = String(text);
  }

  function setMsg(text, className) {
    if (msgEl) {
      msgEl.textContent = text || "";
      msgEl.className = "pa-message " + (className || "");
    }
  }

  function parseJsonSafe(raw) {
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  function getSelectedExercisesFromSummary(summary) {
    if (!summary) return [];

    // 1) Explicit selected list
    if (Array.isArray(summary.selected_exercises)) {
      return summary.selected_exercises
        .map((n) => (n != null ? String(n) : ""))
        .filter((n) => n.trim().length > 0);
    }

    // 2) summary.exercises (array of names OR objects)
    if (Array.isArray(summary.exercises)) {
      if (summary.exercises.length > 0) {
        if (typeof summary.exercises[0] === "string") {
          return summary.exercises
            .map((n) => (n != null ? String(n) : ""))
            .filter((n) => n.trim().length > 0);
        }
        return summary.exercises
          .map((ex) =>
            ex && ex.exercise_name != null ? String(ex.exercise_name) : ""
          )
          .filter((n) => n.trim().length > 0);
      }
    }

    // 3) Keys of exercise_breakdown / exercise_metrics
    const breakdown = summary.exercise_breakdown;
    if (Array.isArray(breakdown)) {
      const names = breakdown
        .map((ex) =>
          ex && ex.exercise_name != null ? String(ex.exercise_name) : ""
        )
        .filter((n) => n.trim().length > 0);
      if (names.length) return names;
    } else if (breakdown && typeof breakdown === "object") {
      const keys = Object.keys(breakdown);
      if (keys.length) return keys;
    }

    const metricsObj = summary.exercise_metrics;
    if (Array.isArray(metricsObj)) {
      const names = metricsObj
        .map((ex) =>
          ex && ex.exercise_name != null ? String(ex.exercise_name) : ""
        )
        .filter((n) => n.trim().length > 0);
      if (names.length) return names;
    } else if (metricsObj && typeof metricsObj === "object") {
      const keys = Object.keys(metricsObj);
      if (keys.length) return keys;
    }

    return [];
  }

  function getSelectedExercises(summary) {
    // Prefer values baked into the summary payload
    const fromSummary = getSelectedExercisesFromSummary(summary);
    if (fromSummary.length) {
      return Array.from(new Set(fromSummary));
    }

    // Fallback to what was stored at exercise-selection time
    const stored = parseJsonSafe(
      sessionStorage.getItem("physioai_selected_exercises")
    );
    if (Array.isArray(stored) && stored.length) {
      return Array.from(
        new Set(
          stored
            .map((n) => (n != null ? String(n) : ""))
            .filter((n) => n.trim().length > 0)
        )
      );
    }

    return [];
  }

  function toNumberOrZero(value) {
    const num = Number(value);
    return Number.isFinite(num) ? num : 0;
  }

  const summaryJson = sessionStorage.getItem("physioai_session_summary");

  if (!summaryJson) {
    setText(scoreEl, "0.00 / 100");
    setText(totalEl, "0");
    setMsg("Session summary not found. Showing defaults.", "");
  } else {
    const summary = parseJsonSafe(summaryJson);

    if (!summary) {
      setText(scoreEl, "0.00 / 100");
      setText(totalEl, "0");
      setMsg("Unable to read session summary. Showing defaults.", "");
      return;
    }

    console.log("PhysioAI summary object:", summary);

    const selectedExercises = getSelectedExercises(summary);

    if (!selectedExercises.length) {
      setText(scoreEl, "0.00 / 100");
      setText(totalEl, "0");
      setMsg("No exercises were selected for this session.", "");
      // No rows rendered if nothing selected
      return;
    }

    // Build metrics map only for selected exercises
    const metricsByExercise = {};
    selectedExercises.forEach((name) => {
      metricsByExercise[name] = defaultMetrics();
    });

    const breakdownRaw =
      summary.exercise_breakdown ??
      summary.exercises ??
      summary.exercise_metrics ??
      [];

    const parsed = Array.isArray(breakdownRaw)
      ? breakdownRaw
      : Object.entries(breakdownRaw || {}).map(([exercise_name, metrics]) => {
          const totalReps = toNumberOrZero(metrics?.total_reps);
          const correctReps = toNumberOrZero(metrics?.correct_reps);
          const incorrectReps =
            typeof metrics?.incorrect_reps === "number"
              ? toNumberOrZero(metrics.incorrect_reps)
              : Math.max(totalReps - correctReps, 0);
          return {
            exercise_name: String(exercise_name || ""),
            total_reps: totalReps,
            correct_reps: correctReps,
            incorrect_reps: incorrectReps,
            posture_correctness_ratio: toNumberOrZero(
              metrics?.posture_correctness_ratio
            ),
          };
        });

    parsed.forEach((item) => {
      const name = item.exercise_name;
      if (!name || !(name in metricsByExercise)) return;
      metricsByExercise[name] = {
        correct_reps: toNumberOrZero(item.correct_reps),
        incorrect_reps: toNumberOrZero(item.incorrect_reps),
        total_reps: toNumberOrZero(item.total_reps),
        posture_correctness_ratio: toNumberOrZero(
          item.posture_correctness_ratio
        ),
      };
    });

    // Compute totals and overall score using only selected exercises
    let totalCorrect = 0;
    let totalIncorrect = 0;
    let totalReps = 0;

    selectedExercises.forEach((name) => {
      const m = metricsByExercise[name] || defaultMetrics();
      const correct = toNumberOrZero(m.correct_reps);
      const incorrect = toNumberOrZero(m.incorrect_reps);
      const total = toNumberOrZero(m.total_reps);

      totalCorrect += correct;
      totalIncorrect += incorrect;
      totalReps += total;
    });

    let rawScore = 0;
    if (totalReps > 0) {
      rawScore = toNumberOrZero((totalCorrect / totalReps) * 100);
    } else {
      rawScore = 0;
    }

    const scoreDisplay = Number.isFinite(rawScore)
      ? rawScore.toFixed(2)
      : "0.00";

    setText(scoreEl, scoreDisplay + " / 100");
    setText(totalEl, totalReps);

    setMsg("Session summary loaded.", "success");

    // Render table rows for selected exercises only
    if (tableBody) {
      // Clear any existing rows defensively
      tableBody.innerHTML = "";
      selectedExercises.forEach((name) => {
        const m = metricsByExercise[name] || defaultMetrics();
        const correct = toNumberOrZero(m.correct_reps);
        const incorrect = toNumberOrZero(m.incorrect_reps);
        const total = toNumberOrZero(m.total_reps);
        const postureRatio = toNumberOrZero(m.posture_correctness_ratio);
        const posturePct = Number.isFinite(postureRatio)
          ? Math.round(postureRatio * 100)
          : 0;

        const tr = document.createElement("tr");
        tr.innerHTML = `
      <td>${name}</td>
      <td>${correct}</td>
      <td>${incorrect}</td>
      <td>${total}</td>
      <td>${posturePct}%</td>
    `;
        tableBody.appendChild(tr);
      });
    }
  }
});
