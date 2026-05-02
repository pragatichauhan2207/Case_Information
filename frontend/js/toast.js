// ============================================================
// js/toast.js  — Global toast notification helper
// Usage: showToast("message", "success" | "error" | "info")
// Requires <div id="toast"></div> in the page.
// ============================================================

function showToast(message, type) {
  type = type || "info";
  var toast = document.getElementById("toast");
  if (!toast) return;

  // Reset, set new type class and message
  toast.className = "show toast-" + type;
  toast.textContent = message;

  // Auto-hide after 3 seconds
  clearTimeout(toast._hideTimer);
  toast._hideTimer = setTimeout(function () {
    toast.className = "";
  }, 3000);
}
