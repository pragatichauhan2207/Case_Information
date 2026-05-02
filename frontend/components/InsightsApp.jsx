// ============================================================
// components/InsightsApp.jsx
// React component for the Insights / Dashboard page.
// Uses Chart.js (CDN) for bar charts.
// ============================================================

const { useState, useEffect, useRef } = React;

// ── Sub-component: KPI stat card ──────────────────────────
function StatCard({ icon, value, label, colorClass }) {
  return (
    <div className="stat-card">
      <div className={"stat-icon stat-icon-" + colorClass}>{icon}</div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}

// ── Sub-component: Bar chart wrapper using Chart.js ───────
function BarChartCanvas({ id, labels, values, color, label }) {
  const canvasRef = useRef(null);
  const chartRef  = useRef(null);

  useEffect(() => {
    // Destroy previous chart instance to avoid duplicate-canvas error
    if (chartRef.current) chartRef.current.destroy();

    const ctx = canvasRef.current.getContext("2d");
    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label:           label,
          data:            values,
          backgroundColor: color,
          borderRadius:    4,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => " " + ctx.parsed.y + " judgments" } },
        },
        scales: {
          x: { ticks: { font: { size: 11 } } },
          y: { ticks: { font: { size: 11 } }, beginAtZero: true },
        },
      },
    });

    // Cleanup on unmount
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [labels, values]); // eslint-disable-line

  return <canvas ref={canvasRef} style={{ maxHeight: "300px" }} />;
}

// ── Sub-component: Horizontal bar chart for judges ────────
function HBarChartCanvas({ id, labels, values }) {
  const canvasRef = useRef(null);
  const chartRef  = useRef(null);

  useEffect(() => {
    if (chartRef.current) chartRef.current.destroy();

    const ctx = canvasRef.current.getContext("2d");
    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label:           "Cases",
          data:            values,
          backgroundColor: "#e8a020",
          borderRadius:    4,
        }],
      },
      options: {
        indexAxis: "y",      // horizontal bar
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 11 } }, beginAtZero: true },
          y: { ticks: { font: { size: 10 } } },
        },
      },
    });
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [labels, values]); // eslint-disable-line

  return <canvas ref={canvasRef} style={{ maxHeight: "340px" }} />;
}

// ── Main InsightsApp component ────────────────────────────
function InsightsApp() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/insights/")
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d => setData(d))
      .catch(() => showToast("Could not load insights. Is backend running?", "error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>;

  if (!data) return (
    <div className="empty-state">
      <div className="empty-icon">⚠️</div>
      <p>No data available. Make sure the Flask backend is running.</p>
    </div>
  );

  // Shorten judge names for the chart label
  const judgeLabels = data.judge_counts.labels.map(name =>
    name.replace(/Hon('|')ble\s+(Mr\.|Ms\.|Mrs\.)?\s*(Justice\s+)?/i, "").substring(0, 28)
  );

  return (
    <div>
      {/* KPI Stat Cards */}
      <div className="stats-grid">
        <StatCard icon="📋" value={data.total_judgments.toLocaleString()} label="Total Judgments" colorClass="primary" />
        <StatCard icon="📅" value={data.oldest_case}  label="Oldest Case"      colorClass="accent"  />
        <StatCard icon="🆕" value={data.newest_case}  label="Most Recent Case" colorClass="success" />
      </div>

      {/* Year-wise chart */}
      <div className="card chart-card">
        <h2 className="chart-title">📊 Year-wise Judgment Count</h2>
        <BarChartCanvas
          id="yearChart"
          labels={data.year_counts.labels}
          values={data.year_counts.values}
          color="#003366"
          label="Judgments"
        />
      </div>

      {/* Top judges chart */}
      <div className="card chart-card">
        <h2 className="chart-title">👨‍⚖️ Top 10 Judges by Case Count</h2>
        <HBarChartCanvas
          id="judgeChart"
          labels={judgeLabels}
          values={data.judge_counts.values}
        />
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<InsightsApp />);
