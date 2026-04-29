/**
 * Smart Expressway – main.js
 * Handles UI interactions, auto-dismiss alerts, and form UX.
 */

document.addEventListener("DOMContentLoaded", () => {

  // ── Auto-dismiss flash alerts after 5 seconds ───────────────────
  document.querySelectorAll(".alert").forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-8px)";
      alert.style.transition = "opacity 0.4s, transform 0.4s";
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // ── Highlight the active nav link ───────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.style.color = "var(--text)";
      link.style.background = "rgba(255,255,255,0.06)";
    }
  });

  // ── Route form: capitalise first letters ─────────────────────────
  ["source", "destination"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("blur", () => {
      el.value = el.value
        .split(" ")
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
    });
  });

  // ── Emergency form: confirm before submit ────────────────────────
  const emergencyForm = document.querySelector(".auth-form");
  if (window.location.pathname === "/emergency" && emergencyForm) {
    emergencyForm.addEventListener("submit", e => {
      const confirmed = confirm(
        "⚠️ Are you sure you want to report an emergency?\n\nThis will alert authorities immediately."
      );
      if (!confirmed) e.preventDefault();
    });
  }

  // ── Smooth scroll for same-page anchors ─────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", e => {
      const target = document.querySelector(anchor.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

});
