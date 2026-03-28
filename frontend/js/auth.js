const API = "http://localhost:5000";

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("login-form")) {
    initLogin();
  }

  if (document.getElementById("signup-form")) {
    initSignup();
  }
});

function initLogin() {
  const form = document.getElementById("login-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch(`${API}/login`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!res.ok) throw new Error("Invalid login");

      window.location.href = "exercises.html";
    } catch (err) {
      document.getElementById("error").innerText = "Login failed";
    }
  });
}

function initSignup() {
  const form = document.getElementById("signup-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const gender = document.getElementById("gender").value;
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm").value;

    if (password !== confirm) {
      document.getElementById("error").innerText = "Passwords do not match";
      return;
    }

    try {
      const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, age, gender, password })
      });

      if (!res.ok) throw new Error("Signup failed");

      window.location.href = "index.html";
    } catch (err) {
      document.getElementById("error").innerText = "Signup failed";
    }
  });
}
