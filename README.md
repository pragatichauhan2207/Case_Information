#  Justice Portal — Sikkim High Court Judgment Search System

Full-stack web application for searching and analysing Sikkim High Court judgments.

---

##  Tech Stack

| Layer     | Technology                                         |
|-----------|----------------------------------------------------|
| Backend   | Python 3, Flask, Flask-CORS, Pandas               |
| Frontend  | HTML5 + CSS3 + Vanilla JS                         |
| React     | React 18 via **CDN**    |
| Charts    | Chart.js via CDN                                  |
| JSX       | Babel Standalone (in-browser transpile)           |
| Data      | CSV flat file (2,400+ judgment records)           |

> **No Node.js, no npm, no build step required.**
> React is loaded directly in the browser via unpkg CDN.

---

##  Project Structure

```
JusticePortal/
│
├── backend/                         # Flask REST API
│   ├── app.py                       # Entry point — also serves frontend files
│   ├── judgment_data.csv            # 2,400+ court records
│   ├── requirements.txt
│   ├── routes/
│   │   ├── judgments.py             # GET /api/judgments/search, /years
│   │   ├── insights.py              # GET /api/insights/
│   │   └── feedback.py              # POST/GET /api/feedback/
│   └── services/
│       ├── data_service.py          # CSV loading, search, aggregation
│       └── feedback_service.py      # In-memory feedback store
│
├── frontend/                        # Pure HTML + CSS + JS + React (CDN)
│   ├── index.html                   # Home page   (HTML only)
│   ├── search.html                  # Search page (React mounts here)
│   ├── insights.html                # Dashboard   (React + Chart.js)
│   ├── feedback.html                # Feedback    (React mounts here)
│   ├── about.html                   # About page  (HTML only)
│   ├── css/
│   │   └── style.css                # All styles — CSS variables
│   ├── js/
│   │   ├── navbar.js                # Shared: hamburger + active link
│   │   └── toast.js                 # Shared: showToast() helper
│   └── components/
│       ├── SearchApp.jsx            # React: search form + table + pagination
│       ├── InsightsApp.jsx          # React: stat cards + Chart.js charts
│       └── FeedbackApp.jsx          # React: form with validation
│
├── docs/
│   └── documentation.md
└── README.md
```

---

##  Setup & Run (Only Python Needed!)

### 1. Install Python dependencies

```bash
cd backend
python -m venv venv

# Activate:
# Windows:    venv\Scripts\activate
# Mac/Linux:  source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Flask

```bash
python app.py
```

### 3. Open Browser

```
http://localhost:5000
```

**That's it.** Flask serves both the API and the HTML/React frontend.
No npm, no Node.js, no build step.

---

##  API Endpoints

| Method | Endpoint                        | Description                        |
|--------|---------------------------------|------------------------------------|
| GET    | `/api/judgments/search`         | Search with q, search_by, year, page |
| GET    | `/api/judgments/years`          | List all available years           |
| GET    | `/api/insights/`                | Dashboard stats + chart data       |
| POST   | `/api/feedback/`                | Submit feedback                    |
| GET    | `/api/feedback/`                | List all feedback                  |

---

##  Features

-  Search by petitioner name or case number
- Year filter dropdown
-  Insights dashboard (bar charts with Chart.js)
-  Direct PDF & HTML document links
-  Feedback form with validation
-  Toast notifications
-  Pagination (20 results/page)
-  Responsive mobile design

---

## How React Works Without npm

Each interactive page loads React from CDN:
```html
<script src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script type="text/babel" src="components/SearchApp.jsx"></script>
```
Babel processes the JSX live in the browser. No compilation step needed.
