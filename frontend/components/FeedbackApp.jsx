// ============================================================
// components/FeedbackApp.jsx
// React component for the Feedback page.
// ============================================================

const { useState } = React;

const INITIAL_FORM = { name: "", email: "", message: "" };

function FeedbackApp() {
  const [form,      setForm]      = useState(INITIAL_FORM);
  const [loading,   setLoading]   = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errors,    setErrors]    = useState([]);

  // Update one field at a time
  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors([]);
  }

  function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setErrors([]);

    fetch("/api/feedback/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(form),
    })
      .then(r => r.json().then(data => ({ ok: r.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) {
          // Backend sends array of error strings
          setErrors(Array.isArray(data.error) ? data.error : [data.error]);
        } else {
          setSubmitted(true);
          setForm(INITIAL_FORM);
          showToast("Feedback submitted! Thank you 🙏", "success");
        }
      })
      .catch(() => showToast("Submission failed. Please try again.", "error"))
      .finally(() => setLoading(false));
  }

  // ── Success state ─────────────────────────────────────────
  if (submitted) {
    return (
      <div className="card feedback-card">
        <div style={{ textAlign: "center", padding: "48px 0" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>✅</div>
          <h2 style={{ color: "var(--primary)", marginBottom: "8px" }}>Thank You!</h2>
          <p style={{ color: "var(--text-muted)", marginBottom: "24px" }}>
            Your feedback has been received. We really appreciate it.
          </p>
          <button className="btn btn-primary" onClick={() => setSubmitted(false)}>
            Submit Another
          </button>
        </div>
      </div>
    );
  }

  // ── Form state ────────────────────────────────────────────
  return (
    <div className="card feedback-card">
      {/* Validation errors */}
      {errors.length > 0 && (
        <div className="error-box show">
          {errors.map((err, i) => <p key={i}>⚠ {err}</p>)}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Your Name *</label>
          <input
            className="form-input"
            type="text"
            name="name"
            placeholder="e.g. Rohan Sharma"
            value={form.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Email Address *</label>
          <input
            className="form-input"
            type="email"
            name="email"
            placeholder="e.g. rohan@example.com"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Message *</label>
          <textarea
            className="form-textarea"
            name="message"
            rows="5"
            placeholder="Share your feedback, suggestions, or report any issues..."
            value={form.message}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Submitting…" : "📨 Submit Feedback"}
        </button>
      </form>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<FeedbackApp />);
