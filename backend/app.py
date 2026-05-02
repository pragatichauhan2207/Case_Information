# ============================================================
# app.py - Main Flask Application Entry Point
# Justice Portal — Sikkim High Court Judgment Search System
# ============================================================

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.judgments import judgments_bp
from routes.insights  import insights_bp
from routes.feedback  import feedback_bp

# Absolute path to the frontend folder (one level up from backend/)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def create_app():
    """
    Application factory.
    Flask serves the HTML/CSS/JS frontend files directly,
    so no separate web server or npm is needed.
    """
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,   # serve static files from frontend/
        static_url_path=""            # at the root URL path
    )

    # Allow cross-origin API requests (useful if served separately)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register API Blueprints ──────────────────────────────
    app.register_blueprint(judgments_bp, url_prefix="/api/judgments")
    app.register_blueprint(insights_bp,  url_prefix="/api/insights")
    app.register_blueprint(feedback_bp,  url_prefix="/api/feedback")

    # ── Serve the frontend HTML pages ────────────────────────
    @app.route("/")
    def home():
        """Serve the homepage."""
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        """
        Serve any frontend file (HTML, CSS, JS, components).
        e.g.  /search.html       → frontend/search.html
              /css/style.css     → frontend/css/style.css
              /components/SearchApp.jsx
        """
        return send_from_directory(FRONTEND_DIR, filename)

    # ── Global error handlers ────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        # Return JSON for API routes, HTML page otherwise
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n Justice Portal is running!")
    print("   Open your browser at:  http://localhost:5000\n")
    app.run(debug=True, port=5000)
