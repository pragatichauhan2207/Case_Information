# ============================================================
# routes/judgments.py
# All API endpoints related to searching & listing judgments.
# ============================================================

from flask import Blueprint, request, jsonify
from services.data_service import search_judgments, get_available_years

# Blueprint groups related routes under a common prefix (/api/judgments)
judgments_bp = Blueprint("judgments", __name__)


@judgments_bp.route("/search", methods=["GET"])
def search():
    """
    GET /api/judgments/search
    Query params:
      - q         : search text (optional)
      - search_by : 'petitioner' | 'case_number'  (default: petitioner)
      - year      : filter by year, e.g. 2020       (optional)
      - page      : page number, default 1
      - per_page  : results per page, default 20
    """
    q          = request.args.get("q", "").strip()
    search_by  = request.args.get("search_by", "petitioner")
    year       = request.args.get("year", "").strip()
    page       = int(request.args.get("page", 1))
    per_page   = int(request.args.get("per_page", 20))

    # Validate search_by value
    if search_by not in ("petitioner", "case_number"):
        return jsonify({"error": "search_by must be 'petitioner' or 'case_number'"}), 400

    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    result = search_judgments(q, search_by, year, page, per_page)
    return jsonify(result), 200


@judgments_bp.route("/years", methods=["GET"])
def years():
    """
    GET /api/judgments/years
    Returns the list of all years available in the dataset.
    Used to populate the year-filter dropdown in the UI.
    """
    year_list = get_available_years()
    return jsonify({"years": year_list}), 200
