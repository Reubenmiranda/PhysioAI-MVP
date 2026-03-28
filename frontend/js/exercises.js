const API_BASE = "http://localhost:5000";

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

function showExercisesMessage(text, type = "") {
  const el = document.getElementById("exercises-message");
  el.textContent = text;
  el.className = `pa-message ${type}`;
}

function updateStartButtonState() {
  const checkboxes = document.querySelectorAll(".exercise-checkbox");
  const selected = Array.from(checkboxes).filter((cb) => cb.checked);
  const btn = document.getElementById("start-session-btn");
  btn.disabled = selected.length !== 5;

  const helper = document.getElementById("exercise-helper");
  helper.textContent = `Selected ${selected.length} / 5 exercises.`;
}

document.addEventListener("DOMContentLoaded", async () => {
  const listEl = document.getElementById("exercise-list");
  const startBtn = document.getElementById("start-session-btn");
  const historyBtn = document.getElementById("session-history-btn");

  if (historyBtn) {
    historyBtn.addEventListener("click", () => {
      window.location.href = "history.html";
    });
  }

  // Fetch exercises
  const { ok, status, data } = await apiGet("/exercises");

  if (!ok) {
    if (status === 401) {
      // Not logged in, redirect to login
      window.location.href = "index.html";
      return;
    }
    showExercisesMessage(
      data.error || "Failed to load exercises. Please try again.",
      "error"
    );
    return;
  }

  const exercises = data.exercises || [];

  if (!exercises.length) {
    showExercisesMessage("No exercises available.", "error");
    return;
  }

  // Render list
  exercises.forEach((ex, index) => {
    const item = document.createElement("label");
    item.className = "pa-exercise-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "exercise-checkbox";
    checkbox.value = ex.name;
    checkbox.id = `exercise-${index}`;

    const details = document.createElement("div");

    const title = document.createElement("div");
    title.className = "pa-exercise-title";
    title.textContent = ex.name;

    const desc = document.createElement("div");
    desc.className = "pa-exercise-desc";
    desc.textContent = ex.description || "";

    details.appendChild(title);
    details.appendChild(desc);

    item.appendChild(checkbox);
    item.appendChild(details);

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        item.classList.add("selected");
      } else {
        item.classList.remove("selected");
      }
      updateStartButtonState();
    });

    listEl.appendChild(item);
  });

  updateStartButtonState();

  startBtn.addEventListener("click", async () => {
    showExercisesMessage("");
    const selected = Array.from(
      document.querySelectorAll(".exercise-checkbox:checked")
    ).map((cb) => cb.value);

    if (selected.length !== 5) {
      showExercisesMessage("Please select exactly 5 exercises.", "error");
      return;
    }

    const { ok: okStart, data: startData } = await apiPost("/session/start", {
      exercises: selected,
    });

    if (!okStart) {
      showExercisesMessage(
        startData.error || "Failed to start session. Please try again.",
        "error"
      );
      return;
    }

    // Save selected exercises for reference (optional)
    sessionStorage.setItem("physioai_selected_exercises", JSON.stringify(selected));

    // Redirect to live session
    window.location.href = "session.html";
  });
});

