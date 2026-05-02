// ============================================================
// js/navbar.js  — Shared navbar: hamburger toggle + active link
// Include this in every HTML page.
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

  // ── Mobile hamburger toggle ──────────────────────────────
  var btn  = document.getElementById("hamburger");
  var menu = document.getElementById("mobileMenu");
  if (btn && menu) {
    btn.addEventListener("click", function () {
      menu.classList.toggle("open");
    });
  }

  // ── Highlight the active nav link ────────────────────────
  var page = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-link, .mobile-menu a").forEach(function (link) {
    if (link.getAttribute("href").split("/").pop() === page) {
      link.classList.add("active");
    }
  });
});
