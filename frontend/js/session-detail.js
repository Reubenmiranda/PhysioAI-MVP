document.addEventListener("DOMContentLoaded", () => {
  const scoreEl = document.getElementById("overall-score");
  const totalEl = document.getElementById("total-reps");
  const dateEl = document.getElementById("session-date");
  const tbody = document.getElementById("detail-tbody");

  function setText(el, text) {
    if (el) el.textContent = String(text);
  }

  function toNum(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  const raw = sessionStorage.getItem("physioai_history_detail");
  if (!raw) {
    setText(scoreEl, "0.00 / 100");
    setText(totalEl, "0");
    setText(dateEl, "Session data not found.");
    return;
  }

  let session;
  try {
    session = JSON.parse(raw);
  } catch (e) {
    setText(dateEl, "Unable to read session data.");
    return;
  }

  // Date
  const dateVal = session.date ? new Date(session.date) : null;
  setText(dateEl, dateVal && !isNaN(dateVal) ? dateVal.toLocaleString() : "Unknown date");

  // Score
  const score = toNum(session.overall_score);
  setText(scoreEl, score.toFixed(2) + " / 100");

  // Total reps
  setText(totalEl, toNum(session.total_reps));

  // Exercise breakdown
  if (!tbody) return;
  tbody.innerHTML = "";

  const metrics = session.per_exercise_metrics;
  const exerciseNames = Array.isArray(session.exercises) ? session.exercises : [];

  if (!metrics || !exerciseNames.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td colspan="5" class="px-8 py-6 text-center text-on-surface-variant">No exercise data recorded.</td>`;
    tbody.appendChild(tr);
    return;
  }

  exerciseNames.forEach((name) => {
    const m = metrics[name] || {};
    const correct = toNum(m.correct_reps);
    const incorrect = toNum(m.incorrect_reps);
    const total = toNum(m.total_reps);
    const posturePct = Math.round(toNum(m.posture_correctness_ratio) * 100);

    const tr = document.createElement("tr");
    tr.className = "hover:bg-surface-container-low/40 transition-colors";
    tr.innerHTML = `
      <td class="px-8 py-4 font-medium text-on-surface">${name}</td>
      <td class="px-8 py-4 text-center text-primary font-bold">${correct}</td>
      <td class="px-8 py-4 text-center text-error">${incorrect}</td>
      <td class="px-8 py-4 text-center">${total}</td>
      <td class="px-8 py-4 text-center">${posturePct}%</td>
    `;
    tbody.appendChild(tr);
  });
});
