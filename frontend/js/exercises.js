const API_BASE = API_CONFIG.baseUrl;

const EXERCISE_ICONS = {
  "Standing Hip Flexion":        { icon: "directions_walk",    bg: "#e0f5f5" },
  "Glute Bridge":                { icon: "self_improvement",   bg: "#e8f4f0" },
  "Cobra Pose":                  { icon: "sports_gymnastics",  bg: "#fef3e2" },
  "Standing March":              { icon: "directions_run",     bg: "#e8eef6" },
  "Standing Forward Arm Raise":  { icon: "front_hand",         bg: "#f0eff8" },
  "Standing Lateral Arm Raise":  { icon: "waving_hand",        bg: "#fde8ea" },
  "Shoulder Shrugs":             { icon: "accessibility",      bg: "#e2f0fb" },
  "Standing Trunk Side Bend":    { icon: "accessibility_new",  bg: "#f0f8e2" },
  "Standing Arm Circles":        { icon: "rotate_right",       bg: "#fdf0e8" },
  "Neutral Posture Hold":        { icon: "person",             bg: "#e8f5e9" },
};

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

function showModal(message) {
  const modal = document.getElementById("selection-modal");
  const msg = document.getElementById("modal-message");
  if (msg) msg.textContent = message;
  if (modal) modal.classList.remove("hidden");
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

  const modalClose = document.getElementById("modal-close");
  if (modalClose) {
    modalClose.addEventListener("click", () => {
      document.getElementById("selection-modal").classList.add("hidden");
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

    // Icon thumbnail
    const iconInfo = EXERCISE_ICONS[ex.name] || { icon: "fitness_center", bg: "#e8eef6" };
    const iconWrap = document.createElement("div");
    iconWrap.style.cssText = `width:3rem;height:3rem;border-radius:0.75rem;background:${iconInfo.bg};display:flex;align-items:center;justify-content:center;flex-shrink:0;`;
    const iconEl = document.createElement("span");
    iconEl.className = "material-symbols-outlined";
    iconEl.style.cssText = "color:#006a71;font-size:1.5rem;font-variation-settings:'FILL' 1;";
    iconEl.textContent = iconInfo.icon;
    iconWrap.appendChild(iconEl);

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
    item.appendChild(iconWrap);
    item.appendChild(details);

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        const currentSelected = Array.from(document.querySelectorAll(".exercise-checkbox:checked"));
        if (currentSelected.length > 5) {
          checkbox.checked = false;
          showModal("You can only select 5 exercises. Please deselect one before choosing another.");
          return;
        }
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
      showModal("Please select exactly 5 exercises to proceed.");
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

