// ============================================================
// components/SearchApp.jsx
// React component for the Search page.
// Loaded via CDN React + Babel — no npm/node required.
// ============================================================

const { useState, useEffect } = React;

// ── Helper: escape HTML to prevent XSS ───────────────────
function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ── Sub-component: one table row ─────────────────────────
function JudgmentRow({ row }) {
  return (
    <tr>
      <td><span className="badge badge-primary">{row.case_number}</span></td>
      <td>{row.petitioner}</td>
      <td>{row.respondent}</td>
      <td style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{row.judge}</td>
      <td>{row.date}</td>
      <td>
        <div className="doc-links">
          {row.pdf_link && (
            <a href={row.pdf_link} target="_blank" rel="noreferrer" className="doc-btn doc-btn-pdf">
              📄 PDF
            </a>
          )}
          {row.html_link && (
            <a href={row.html_link} target="_blank" rel="noreferrer" className="doc-btn doc-btn-html">
              🌐 HTML
            </a>
          )}
        </div>
      </td>
    </tr>
  );
}

// ── Sub-component: results table ──────────────────────────
function JudgmentTable({ results }) {
  if (results.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📂</div>
        <p>No judgments found. Try a different search.</p>
      </div>
    );
  }
  return (
    <div className="table-wrapper">
      <table className="judgment-table">
        <thead>
          <tr>
            <th>Case Number</th>
            <th>Petitioner</th>
            <th>Respondent</th>
            <th>Judge</th>
            <th>Date</th>
            <th>Documents</th>
          </tr>
        </thead>
        <tbody>
          {results.map((row, i) => <JudgmentRow key={i} row={row} />)}
        </tbody>
      </table>
    </div>
  );
}

// ── Sub-component: pagination ─────────────────────────────
function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  // Build array of page numbers (max 5 around current)
  const getPages = () => {
    let start = Math.max(1, page - 2);
    let end   = Math.min(totalPages, start + 4);
    start     = Math.max(1, end - 4);
    const pages = [];
    for (let p = start; p <= end; p++) pages.push(p);
    return pages;
  };

  return (
    <div className="pagination">
      <button
        className="page-btn"
        disabled={page === 1}
        onClick={() => onPageChange(page - 1)}
      >← Prev</button>

      {getPages().map(p => (
        <button
          key={p}
          className={"page-btn" + (p === page ? " active" : "")}
          onClick={() => onPageChange(p)}
        >{p}</button>
      ))}

      <button
        className="page-btn"
        disabled={page === totalPages}
        onClick={() => onPageChange(page + 1)}
      >Next →</button>
    </div>
  );
}

// ── Main SearchApp component ───────────────────────────────
function SearchApp() {
  const [query,      setQuery]      = useState("");
  const [searchBy,   setSearchBy]   = useState("petitioner");
  const [yearFilter, setYearFilter] = useState("");
  const [years,      setYears]      = useState([]);
  const [results,    setResults]    = useState([]);
  const [total,      setTotal]      = useState(0);
  const [page,       setPage]       = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading,    setLoading]    = useState(false);
  const [searched,   setSearched]   = useState(false);

  // Fetch available years on first render
  useEffect(() => {
    fetch("/api/judgments/years")
      .then(r => r.json())
      .then(data => setYears(data.years))
      .catch(() => showToast("Could not load year filters. Is backend running?", "error"));
  }, []);

  // Re-run search when page changes (after initial search)
  useEffect(() => {
    if (searched) runSearch(page);
  }, [page]); // eslint-disable-line

  // ── Core fetch function ────────────────────────────────
  function runSearch(targetPage) {
    setLoading(true);
    const params = new URLSearchParams({
      q:         query,
      search_by: searchBy,
      year:      yearFilter,
      page:      targetPage,
      per_page:  20,
    });

    fetch("/api/judgments/search?" + params)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => {
        setResults(data.results);
        setTotal(data.total);
        setPage(data.page);
        setTotalPages(data.total_pages);
        if (data.total === 0) showToast("No matching judgments found.", "info");
      })
      .catch(() => showToast("Search failed. Is the backend running?", "error"))
      .finally(() => setLoading(false));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setSearched(true);
    setPage(1);
    runSearch(1);
  }

  function handleReset() {
    setQuery(""); setSearchBy("petitioner"); setYearFilter("");
    setResults([]); setTotal(0); setPage(1); setTotalPages(0); setSearched(false);
  }

  function handlePageChange(p) {
    setPage(p);
    window.scrollTo({ top: 300, behavior: "smooth" });
  }

  return (
    <div>
      {/* Search Form */}
      <form className="card" onSubmit={handleSubmit} style={{ marginBottom: "32px" }}>
        <div className="search-row">
          {/* Query input */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Search Term</label>
            <input
              className="form-input"
              type="text"
              placeholder="e.g. Makraj Limboo  or  Crl.A/17/2019"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>

          {/* Search-by dropdown */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Search By</label>
            <select
              className="form-select"
              value={searchBy}
              onChange={e => setSearchBy(e.target.value)}
            >
              <option value="petitioner">Petitioner Name</option>
              <option value="case_number">Case Number</option>
            </select>
          </div>

          {/* Year filter */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Filter by Year</label>
            <select
              className="form-select"
              value={yearFilter}
              onChange={e => setYearFilter(e.target.value)}
            >
              <option value="">All Years</option>
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        {/* Action buttons */}
        <div className="search-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Searching…" : "🔍 Search"}
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleReset}>
            Reset
          </button>
        </div>
      </form>

      {/* Loading spinner */}
      {loading && (
        <div className="spinner-wrap"><div className="spinner" /></div>
      )}

      {/* Results */}
      {!loading && searched && (
        <>
          <p className="results-meta">
            Found <strong>{total}</strong> judgment{total !== 1 ? "s" : ""}
          </p>
          <JudgmentTable results={results} />
          <Pagination page={page} totalPages={totalPages} onPageChange={handlePageChange} />
        </>
      )}
    </div>
  );
}

// Mount this component into <div id="root">
ReactDOM.createRoot(document.getElementById("root")).render(<SearchApp />);
