# ============================================================
# routes/feedback.py
# API endpoints for submitting and viewing feedback.
# ============================================================

from flask import Blueprint, request, jsonify
from services.feedback_service import add_feedback, get_all_feedback

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    """
    POST /api/feedback/
    Body (JSON): { name, email, message }
    Validates required fields and saves the feedback.
    """
    body = request.get_json(silent=True) or {}

    name    = body.get("name", "").strip()
    email   = body.get("email", "").strip()
    message = body.get("message", "").strip()

    # Basic validation
    errors = []
    if not name:
        errors.append("Name is required.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")
    if not message:
        errors.append("Message cannot be empty.")

    if errors:
        return jsonify({"error": errors}), 400

    entry = add_feedback(name, email, message)
    return jsonify({"message": "Feedback submitted successfully!", "entry": entry}), 201


@feedback_bp.route("/", methods=["GET"])
def list_feedback():
    """
    GET /api/feedback/
    Returns all submitted feedback (admin view).
    """
    return jsonify({"feedback": get_all_feedback()}), 200
