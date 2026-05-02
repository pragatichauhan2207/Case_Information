# ============================================================
# services/judgment_service.py
# ============================================================
# This is the "brain" of the backend.
# All CSV reading and business logic lives here.
# Routes call these functions — they never touch the CSV directly.
# ============================================================

import os
import pandas as pd

# Path to the data file (relative to this file's parent directory)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "judgment_data.csv")


def _load_data() -> pd.DataFrame:
    """
    Load and normalize the CSV into a DataFrame.
    Called every time we need data (simple for a project this size).
    In a production app you'd cache this in memory or use a database.
    """
    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    # Rename columns to clean snake_case keys used in API responses
    df = df.rename(columns={
        "Judgment Date": "date",
        "Judge":         "judge",
        "Case Number":   "case_number",
        "Petitioner":    "petitioner",
        "Respondent":    "respondent",
        "PDF Link":      "pdf_link",
        "HTML Link":     "html_link",
    })

    # Parse the date column; invalid dates become NaT (Not a Time)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Extract year as integer (useful for filtering)
    df["year"] = df["date"].dt.year

    # Fill NaN strings so JSON serialisation doesn't break
    df = df.fillna("")

    return df


# ── Public functions used by routes ──────────────────────────

def search_judgments(query: str, search_type: str,
                     sort_by: str = "date", order: str = "desc",
                     page: int = 1, per_page: int = 20) -> dict:
    """
    Search judgments by petitioner name or case number.

    Parameters
    ----------
    query       : The search keyword entered by the user.
    search_type : "name" → search Petitioner column
                  "case" → search Case Number column
    sort_by     : Column to sort results ("date", "petitioner", "case_number")
    order       : "asc" or "desc"
    page        : Page number (1-based) for pagination
    per_page    : Results per page

    Returns a dict with keys: results, total, page, per_page, total_pages
    """
    df = _load_data()

    # ── Filter ───────────────────────────────────────────────
    if not query:
        # Empty query → return empty result
        return _paginate(df.head(0), page, per_page)

    if search_type == "name":
        mask = df["petitioner"].str.contains(query, case=False, na=False)
    else:  # "case"
        mask = df["case_number"].astype(str).str.contains(query, case=False, na=False)

    filtered = df[mask].copy()

    # ── Sort ─────────────────────────────────────────────────
    valid_sort_cols = {"date", "petitioner", "case_number"}
    if sort_by not in valid_sort_cols:
        sort_by = "date"

    ascending = order != "desc"
    filtered = filtered.sort_values(sort_by, ascending=ascending)

    return _paginate(filtered, page, per_page)


def get_all_judgments(sort_by: str = "date", order: str = "desc",
                      page: int = 1, per_page: int = 20,
                      year_filter: str = "") -> dict:
    """
    Return all judgments with optional year filter, sort, and pagination.
    Used for the main Browse / Dashboard view.
    """
    df = _load_data()

    # ── Year filter ───────────────────────────────────────────
    if year_filter:
        try:
            yr = int(year_filter)
            df = df[df["year"] == yr]
        except ValueError:
            pass  # Ignore invalid year values

    # ── Sort ─────────────────────────────────────────────────
    valid_sort_cols = {"date", "petitioner", "case_number"}
    if sort_by not in valid_sort_cols:
        sort_by = "date"
    ascending = order != "desc"
    df = df.sort_values(sort_by, ascending=ascending)

    return _paginate(df, page, per_page)


def get_judgment_by_case(case_number: str) -> dict | None:
    """
    Fetch a single judgment by its exact case number.
    Returns None if not found.
    """
    df = _load_data()
    match = df[df["case_number"] == case_number]
    if match.empty:
        return None
    # Return the first match as a plain dict
    row = match.iloc[0].to_dict()
    # Convert Timestamp to string for JSON serialisation
    if pd.notna(row.get("date")) and hasattr(row["date"], "strftime"):
        row["date"] = row["date"].strftime("%d-%m-%Y")
    return row


def get_insights() -> dict:
    """
    Compute summary statistics used on the Insights / Charts page.

    Returns
    -------
    {
      court_counts : { court_name: count },   ← not used (CSV has no Court col)
      year_counts  : { year: count },
      judge_counts : { judge_name: count },
      total        : int,
      latest_year  : int,
    }
    """
    df = _load_data()

    # Year-wise count
    year_counts = (
        df["year"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .to_dict()
    )
    # Convert keys to strings so JSON serialisation is clean
    year_counts = {str(k): v for k, v in year_counts.items()}

    # Judge-wise count (top 15)
    judge_counts = (
        df["judge"]
        .value_counts()
        .head(15)
        .to_dict()
    )

    # Total records
    total = len(df)
    latest_year = int(df["year"].dropna().max()) if not df["year"].dropna().empty else 0

    return {
        "year_counts":  year_counts,
        "judge_counts": judge_counts,
        "total":        total,
        "latest_year":  latest_year,
    }


def get_available_years() -> list:
    """Return sorted list of years present in the dataset."""
    df = _load_data()
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    return years


# ── Helper ───────────────────────────────────────────────────

def _paginate(df: pd.DataFrame, page: int, per_page: int) -> dict:
    """
    Slice a DataFrame into a paginated response dict.
    Converts Timestamp values to strings for safe JSON serialisation.
    """
    total = len(df)
    total_pages = max(1, -(-total // per_page))  # ceiling division
    start = (page - 1) * per_page
    end   = start + per_page
    page_df = df.iloc[start:end].copy()

    # Convert date Timestamp → string
    if "date" in page_df.columns:
        page_df["date"] = page_df["date"].apply(
            lambda d: d.strftime("%d-%m-%Y") if pd.notna(d) and hasattr(d, "strftime") else ""
        )

    # Drop the helper 'year' column from responses
    if "year" in page_df.columns:
        page_df = page_df.drop(columns=["year"])

    return {
        "results":     page_df.to_dict(orient="records"),
        "total":       total,
        "page":        page,
        "per_page":    per_page,
        "total_pages": total_pages,
    }
