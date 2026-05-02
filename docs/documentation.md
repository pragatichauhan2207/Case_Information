# Justice Portal — Project Documentation

## 1. Project Introduction

Justice Portal is a full-stack web application designed to provide an intuitive,
searchable interface for Sikkim High Court judgments. The project digitises and
makes accessible over 2,400 legal case records spanning multiple decades.

The platform serves citizens, legal professionals, researchers, and students who
need quick, reliable access to court judgment data — without requiring knowledge
of legal databases.

---

## 2. Objective

- Provide a free, open-access digital repository of Sikkim High Court judgments
- Enable keyword-based search by petitioner name or case number
- Support year-based filtering for focused research
- Visualise case distribution data through charts and statistics
- Create a maintainable, extensible codebase that can be scaled to other courts

---

## 3. System Architecture

```
┌─────────────────────────────────────────┐
│            USER (Browser)               │
│         React SPA — port 3000           │
└───────────────┬─────────────────────────┘
                │  HTTP /api/* requests
                ▼
┌─────────────────────────────────────────┐
│         Flask REST API — port 5000      │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │   Routes    │  │    Services      │  │
│  │ judgments   │→ │  data_service    │  │
│  │ insights    │  │  feedback_service│  │
│  │ feedback    │  └──────────────────┘  │
│  └─────────────┘           │            │
│                            ▼            │
│                  ┌──────────────────┐   │
│                  │ judgment_data.csv│   │
│                  │  (2,477 records) │   │
│                  └──────────────────┘   │
└─────────────────────────────────────────┘
```

**Layers:**
- **Presentation Layer** — React components, pages, CSS
- **API Layer** — Flask Blueprints, route handlers, validation
- **Service Layer** — Business logic, data processing (Pandas)
- **Data Layer** — CSV flat file (replaceable with a database)

---

## 4. Backend — Detailed Explanation

### 4.1 Entry Point: `app.py`

Uses the Application Factory pattern (`create_app()`) to build the Flask app.
This allows the app to be imported and tested without side effects.

Registers three Blueprints:
- `judgments_bp` → `/api/judgments/*`
- `insights_bp`  → `/api/insights/*`
- `feedback_bp`  → `/api/feedback/*`

### 4.2 Service Layer

#### `services/data_service.py`
The core data processing module. All interactions with the CSV go here.

Key functions:
- `load_data()` — reads CSV into a Pandas DataFrame, normalises column names,
  parses the date column, and extracts a year field.
- `search_judgments(query, search_by, year, page, per_page)` — filters the
  DataFrame by text query and year, then paginates the results.
- `get_insights()` — computes aggregated statistics: total count, year-wise
  distribution, and top-10 judges by case count.
- `get_available_years()` — returns sorted list of all years for the dropdown.

#### `services/feedback_service.py`
An in-memory store for feedback submissions. In production, this would be
replaced with a database (SQLite, PostgreSQL, etc.).

### 4.3 Routes

All route handlers are thin — they only:
1. Extract and validate request parameters
2. Call the appropriate service function
3. Return a JSON response

**`routes/judgments.py`**
- `GET /api/judgments/search` — accepts q, search_by, year, page, per_page
- `GET /api/judgments/years`  — returns available years list

**`routes/insights.py`**
- `GET /api/insights/` — returns aggregated stats and chart-ready data

**`routes/feedback.py`**
- `POST /api/feedback/` — validates and stores feedback
- `GET  /api/feedback/` — returns all feedback entries

### 4.4 Data Model (CSV Columns)

| Column          | Type   | Description                     |
|-----------------|--------|---------------------------------|
| Judgment Date   | string | Date of judgment (DD-MM-YYYY)   |
| Judge           | string | Full name and title of judge    |
| Case Number     | string | Unique case identifier          |
| Petitioner      | string | Name of petitioner/appellant    |
| Respondent      | string | Name of respondent              |
| PDF Link        | URL    | Direct link to judgment PDF     |
| HTML Link       | URL    | Direct link to judgment HTML    |

---

## 5. Frontend — Detailed Explanation

### 5.1 Entry Points

- `public/index.html` — HTML shell, loads Google Fonts
- `src/index.js` — mounts React app inside `<div id="root">`
- `src/App.js` — root component; sets up React Router and the Toast context

### 5.2 Global State: Toast Context

`ToastContext` is a React context that provides a `showToast(message, type)`
function to any component in the tree. This avoids prop-drilling and keeps
notification logic centralised.

### 5.3 API Service Layer: `services/api.js`

All HTTP calls are centralised here using an Axios instance configured with:
- `baseURL: "/api"` — proxied to Flask in development
- `timeout: 10000` — 10-second request timeout

Functions exported:
- `searchJudgments(params)` — GET search with filters
- `fetchYears()` — GET available years
- `fetchInsights()` — GET dashboard data
- `submitFeedback(data)` — POST feedback

### 5.4 Components

| Component        | Purpose                                       |
|------------------|-----------------------------------------------|
| `Navbar`         | Sticky top navigation bar with mobile menu   |
| `Toast`          | Floating notification banner (3s auto-dismiss)|
| `StatCard`       | Reusable KPI card (icon + value + label)      |
| `JudgmentTable`  | Responsive results table with document links |
| `Pagination`     | Page navigator; generates max 5 page buttons |

### 5.5 Pages

| Page       | Route        | Description                              |
|------------|--------------|------------------------------------------|
| `Home`     | `/`          | Hero section + feature cards             |
| `Search`   | `/search`    | Search form, results table, pagination   |
| `Insights` | `/insights`  | KPI cards + two Recharts bar charts      |
| `About`    | `/about`     | Project overview, tech stack, team       |
| `Feedback` | `/feedback`  | Validated feedback form                  |
| `NotFound` | `*`          | 404 fallback page                        |

### 5.6 Styling System

All styles use CSS Custom Properties (variables) defined in `global.css`:
- `--color-primary` (#003366) — navy blue brand colour
- `--color-accent`  (#e8a020) — golden amber accent
- `--space-*` — consistent spacing scale
- `--radius-*` — border-radius tokens
- `--shadow-*` — box-shadow tokens

---

## 6. API Flow Diagram

### Search Flow

```
User types query → clicks "Search"
        │
        ▼
Search.js calls searchJudgments({ q, search_by, year, page })
        │
        ▼  GET /api/judgments/search?q=...&search_by=...
Flask routes/judgments.py → search()
        │
        ▼
services/data_service.py → search_judgments()
  ├─ load_data()    reads CSV into DataFrame
  ├─ text filter    df[col].str.contains(query)
  ├─ year filter    df[year == year]
  ├─ sort           by date descending
  └─ paginate       iloc[start:end]
        │
        ▼
JSON response: { results[], total, page, per_page, total_pages }
        │
        ▼
Search.js updates state → JudgmentTable renders rows
```

### Feedback Submission Flow

```
User fills form → clicks "Submit"
        │
        ▼
Feedback.js calls submitFeedback({ name, email, message })
        │
        ▼  POST /api/feedback/   { name, email, message }
Flask routes/feedback.py → submit_feedback()
  ├─ Validate fields (name, email@, message)
  ├─ Return 400 with errors list if invalid
  └─ Call feedback_service.add_feedback()
        │
        ▼
JSON response: { message: "...", entry: { id, name, ... } }
        │
        ▼
Feedback.js shows success state + Toast notification
```

---

## 7. Architecture Diagrams (Textual)

### Component Tree

```
App
├── Navbar
├── Routes
│   ├── Home        → StatCard (×3), FeatureCard (×6)
│   ├── Search      → JudgmentTable, Pagination
│   ├── Insights    → StatCard (×3), BarChart (×2)
│   ├── About       → TechGrid, TeamGrid
│   └── Feedback    → Form
└── Toast (conditional)
```

### Data Flow (React)

```
api.js (Axios)
    │ async/await
    ▼
Page Component (useState, useEffect)
    │ props
    ▼
Child Components (JudgmentTable, StatCard, Pagination)
    │ events (onClick, onChange)
    ▼
Page Component updates state → re-render
```

---

## 8. How to Extend the Project

1. **Add a database** — Replace `judgment_data.csv` with SQLite using SQLAlchemy.
   Only `data_service.py` needs updating.

2. **Add authentication** — Use Flask-Login or JWT tokens for an admin panel.

3. **Add more courts** — The CSV can include a `court` column, and a court-filter
   dropdown can be added alongside the year filter.

4. **Deploy to production** — Use Gunicorn for Flask and Nginx as a reverse proxy.
   Build the React app with `npm run build` and serve static files.

---

## 9. Conclusion

Justice Portal demonstrates a clean, well-organised full-stack architecture
suitable for a B.Tech Computer Science project. The separation of concerns
between the Flask backend (routes, services, data) and React frontend
(components, pages, services) makes the codebase easy to read, debug, and extend.

Key takeaways:
- Flask Blueprints enable modular, maintainable API routes
- Pandas makes data filtering and aggregation very concise
- React context eliminates prop-drilling for shared state
- CSS variables make consistent theming trivial
- The proxy in `package.json` simplifies local full-stack development
