# Competitor Price Aggregator & Forecasting Tool

A full-stack Flask application to manage properties, simulate competitor price monitoring, visualize analytics, forecast prices, and export reports (CSV/PDF).

## Tech Stack

- **Backend:** Flask (Python)
- **DB:** MySQL (via SQLAlchemy). Works with `mysql+pymysql://...`
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JS (ES6+)
- **Charts:** Chart.js (interactive on the dashboard)
- **Data:** Pandas for manipulation
- **Forecasting:** scikit-learn (Linear Regression)
- **Scraping:** Simulated with BeautifulSoup/Selenium placeholders + robust error handling
- **Reports:** CSV via Pandas; PDF via ReportLab (+ Matplotlib for chart images)

> Date generated: 2025-08-26

---

## Setup

1. **Clone & create venv**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables** (create `.env` in project root):
   ```env
   FLASK_ENV=development
   SECRET_KEY=dev-secret-change-me
   DATABASE_URI=mysql+pymysql://user:password@localhost/competitor_tool_db?charset=utf8mb4
   ```

   - For quick local testing without MySQL, you may *temporarily* use SQLite:
     `DATABASE_URI=sqlite:///app.db`

3. **Initialize DB**
   - **Option A (SQL file):**
     Import `schema.sql` into your MySQL database (phpMyAdmin or MySQL CLI).
   - **Option B (SQLAlchemy create_all):**
     On first run the app will create tables if they don't exist.

4. **Run the app**
   ```bash
   export FLASK_APP=run.py  # Windows: set FLASK_APP=run.py
   flask run
   ```
   - Visit `http://127.0.0.1:5000`

5. **Simulate competitor scraping**
   - From the UI (Dashboard → "Run Scrape") or via CLI:
     ```bash
     python -m app.scrape --user 1 --property 1
     ```

6. **Run forecasting for next 7 days**
   ```bash
   python -m app.forecast --user 1 --property 1
   ```

7. **Generate reports**
   - CSV:
     ```bash
     python -m app.reports csv --user 1 --property 1 --out reports/property_1.csv
     ```
   - PDF:
     ```bash
     python -m app.reports pdf --user 1 --property 1 --out reports/property_1.pdf
     ```

---

## Project Structure

```
competitor_price_tool/
├─ app/
│  ├─ __init__.py            # App factory + DB init
│  ├─ models.py              # SQLAlchemy models
│  ├─ auth.py                # Registration/Login/Logout
│  ├─ properties.py          # CRUD for properties
│  ├─ dashboard.py           # Dashboard + analytics
│  ├─ scrape.py              # Simulated scraping module (CLI & route)
│  ├─ forecast.py            # Linear Regression forecasting (CLI)
│  ├─ reports.py             # CSV/PDF report generation (CLI)
│  ├─ utils.py               # Helpers
│  ├─ templates/
│  └─ static/
├─ schema.sql                # DB schema (MySQL)
├─ requirements.txt
├─ README.md
├─ run.py                    # Entry point
└─ wsgi.py                   # WSGI entry
```

---

## Notes

- Passwords are hashed (Werkzeug) and never stored in plain text.
- Sessions are server-side (Flask session) with secure cookie.
- Scraping is simulated via a local dataset & randomized prices with basic exceptions to mimic failures.
- Forecasts are stored in `forecasts` table per property per date.
- Dashboard shows: your base price vs. average competitor price over time, recent competitor entries, and key metrics.
- Chart.js is loaded via CDN in templates (no extra Python packages needed for charts).

## License

For educational use.