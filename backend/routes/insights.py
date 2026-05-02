# ============================================================
# routes/insights.py
# API endpoints for dashboard charts and statistics.
# ============================================================

from flask import Blueprint, jsonify
from services.data_service import get_insights

insights_bp = Blueprint("insights", __name__)


@insights_bp.route("/", methods=["GET"])
def insights():
    """
    GET /api/insights/
    Returns aggregated data for the dashboard:
      - total_judgments
      - oldest_case / newest_case
      - year_counts  (labels + values for bar chart)
      - judge_counts (labels + values for horizontal bar chart)
    """
    data = get_insights()
    return jsonify(data), 200
