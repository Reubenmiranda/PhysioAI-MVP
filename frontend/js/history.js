document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("history-container");
  const msgEl = document.getElementById("history-message");

  function setText(el, text) {
    if (el) {
      el.textContent = text != null ? String(text) : "";
    }
  }

  function parseHistory(raw) {
    if (!raw) return [];
    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      console.error("Failed to parse session history:", e);
      return [];
    }
  }

  const raw = localStorage.getItem("physioai_session_history");
  const history = parseHistory(raw);

  console.log("Loaded PhysioAI session history:", history);

  if (!history.length) {
    setText(msgEl, "No previous sessions found.");
    if (container) {
      container.innerHTML = "";
    }
    return;
  }

  setText(msgEl, "");

  if (!container) {
    return;
  }

  // Sort newest to oldest by date
  const sorted = history
    .slice()
    .sort((a, b) => {
      const da = new Date(a && a.date ? a.date : 0).getTime();
      const db = new Date(b && b.date ? b.date : 0).getTime();
      return db - da;
    });

  // Use a simple card layout for clarity
  container.innerHTML = "";

  sorted.forEach((session) => {
    const card = document.createElement("div");
    card.className = "pa-card";

    const dateValue = session && session.date ? new Date(session.date) : null;
    const dateText = dateValue && !isNaN(dateValue.getTime())
      ? dateValue.toLocaleString()
      : "Unknown date";

    const overallScore =
      session && session.overall_score != null ? session.overall_score : 0;
    const totalReps =
      session && session.total_reps != null ? session.total_reps : 0;

    const exercises = Array.isArray(session && session.exercises)
      ? session.exercises
      : [];

    const exercisesText = exercises.length
      ? exercises.join(", ")
      : "No exercises recorded";

    card.innerHTML = `
      <h3>Session</h3>
      <p><strong>Date &amp; Time:</strong> ${dateText}</p>
      <p><strong>Overall score:</strong> ${overallScore}</p>
      <p><strong>Total reps:</strong> ${totalReps}</p>
      <p><strong>Exercises performed:</strong> ${exercisesText}</p>
    `;

    container.appendChild(card);
  });
});

