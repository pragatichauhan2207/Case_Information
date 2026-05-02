# ============================================================
# services/data_service.py
# Handles all CSV data loading and querying logic.
# Keeps the route handlers thin — business logic lives here.
# ============================================================

import os
import pandas as pd

# Path to the CSV file (relative to backend/ folder)
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "judgment_data.csv")


def load_data() -> pd.DataFrame:
    """
    Load the judgment CSV into a pandas DataFrame.
    Normalises column names so the rest of the app uses
    consistent snake_case keys.
    """
    df = pd.read_csv(CSV_PATH, encoding="utf-8")

    # Rename CSV columns to clean internal names
    df.rename(columns={
        "Judgment Date": "date",
        "Judge":         "judge",
        "Case Number":   "case_number",
        "Petitioner":    "petitioner",
        "Respondent":    "respondent",
        "PDF Link":      "pdf_link",
        "HTML Link":     "html_link",
    }, inplace=True)

    # Parse date column; invalid values become NaT
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # Extract year for filtering/insights
    df["year"] = df["date"].dt.year.astype("Int64")  # nullable int

    return df


def search_judgments(query: str, search_by: str, year: str, page: int, per_page: int) -> dict:
    """
    Search and filter judgments.

    Parameters
    ----------
    query      : text to search (petitioner name or case number)
    search_by  : 'petitioner' | 'case_number'
    year       : filter by year string, e.g. '2020', or '' for all
    page       : 1-based page number
    per_page   : results per page

    Returns a dict with { results, total, page, per_page, total_pages }
    """
    df = load_data()

    # ── Text search ──────────────────────────────────────
    if query:
        col = "petitioner" if search_by == "petitioner" else "case_number"
        df = df[df[col].astype(str).str.contains(query, case=False, na=False)]

    # ── Year filter ──────────────────────────────────────
    if year and year.isdigit():
        df = df[df["year"] == int(year)]

    # ── Sort newest first ────────────────────────────────
    df = df.sort_values("date", ascending=False, na_position="last")

    total = len(df)

    # ── Pagination ───────────────────────────────────────
    start = (page - 1) * per_page
    end   = start + per_page
    page_df = df.iloc[start:end]

    # ── Convert to JSON-safe list of dicts ───────────────
    records = []
    for _, row in page_df.iterrows():
        records.append({
            "case_number": row["case_number"],
            "petitioner":  row["petitioner"],
            "respondent":  row["respondent"],
            "judge":       row["judge"],
            "date":        row["date"].strftime("%d-%m-%Y") if pd.notna(row["date"]) else "N/A",
            "year":        int(row["year"]) if pd.notna(row["year"]) else None,
            "pdf_link":    row["pdf_link"] if pd.notna(row["pdf_link"]) else None,
            "html_link":   row["html_link"] if pd.notna(row["html_link"]) else None,
        })

    import math
    return {
        "results":     records,
        "total":       total,
        "page":        page,
        "per_page":    per_page,
        "total_pages": math.ceil(total / per_page) if per_page else 1,
    }


def get_insights() -> dict:
    """
    Return aggregated statistics for the Insights dashboard.
    """
    df = load_data()

    # Year-wise count (drop NaT rows)
    year_series = df["year"].dropna().astype(int)
    year_counts = year_series.value_counts().sort_index()

    # Judge-wise count (top 10)
    judge_counts = df["judge"].value_counts().head(10)

    # Total records
    total = len(df)

    # Date range
    valid_dates = df["date"].dropna()
    oldest = valid_dates.min().strftime("%d-%m-%Y") if len(valid_dates) else "N/A"
    newest = valid_dates.max().strftime("%d-%m-%Y") if len(valid_dates) else "N/A"

    return {
        "total_judgments": total,
        "oldest_case":     oldest,
        "newest_case":     newest,
        "year_counts": {
            "labels": [str(y) for y in year_counts.index.tolist()],
            "values": year_counts.values.tolist(),
        },
        "judge_counts": {
            "labels": judge_counts.index.tolist(),
            "values": judge_counts.values.tolist(),
        },
    }


def get_available_years() -> list:
    """Return sorted list of all years present in the dataset."""
    df = load_data()
    years = df["year"].dropna().astype(int).unique()
    return sorted(years.tolist())
