import sqlite3
import datetime
import os
from typing import Optional, Tuple, List
import matplotlib.pyplot as plt

DB_NAME = "expenses.db"
CHART_DIR = os.path.join("static", "charts")
os.makedirs(CHART_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_NAME)


def _iso(date_obj: datetime.date) -> str:
    return date_obj.isoformat()


def _fetch_category_sums(start_date: str, end_date: str) -> List[Tuple[str, float]]:
    """Return list of (category, total_amount) between start_date and end_date (inclusive).
    Dates are ISO strings: YYYY-MM-DD
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category",
        (start_date, end_date),
    )
    data = cur.fetchall()
    conn.close()
    return data


def _fetch_daily_totals(start_date: str, end_date: str) -> List[Tuple[str, float]]:
    """Return list of (date, total_amount) grouped by date ordered ascending.
    Dates are ISO strings.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY date ORDER BY date",
        (start_date, end_date),
    )
    data = cur.fetchall()
    conn.close()
    return data


# --- summary text helpers -------------------------------------------------

def get_weekly_summary_text() -> str:
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    data = _fetch_category_sums(_iso(week_ago), _iso(today))
    if not data:
        return "No expenses recorded in the past week."

    lines = [f"Weekly Summary ({week_ago} to {today}):"]
    total = 0.0
    for category, amount in data:
        total += amount if amount else 0.0
        lines.append(f" - {category}: ₹{amount:.2f}")
    lines.append(f"\nTotal spent this week: ₹{total:.2f}")
    return "\n".join(lines)


def get_monthly_summary_text() -> str:
    today = datetime.date.today()
    start_month = today.replace(day=1)
    data = _fetch_category_sums(_iso(start_month), _iso(today))
    if not data:
        return "No expenses recorded this month."

    lines = [f"Monthly Summary ({start_month} to {today}):"]
    total = 0.0
    for category, amount in data:
        total += amount if amount else 0.0
        lines.append(f" - {category}: ₹{amount:.2f}")
    lines.append(f"\nTotal spent this month: ₹{total:.2f}")
    return "\n".join(lines)


# --- chart generators ----------------------------------------------------

def _save_figure(fig, path: str) -> str:
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_weekly_category_chart() -> Optional[str]:
    """Generate pie chart for last 7 days by category, save PNG, and return path or None."""
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    data = _fetch_category_sums(_iso(week_ago), _iso(today))
    if not data:
        print("No data for weekly category chart.")
        return None

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
    ax.set_title("Weekly Expenses by Category")

    out_path = os.path.join(CHART_DIR, "weekly_category_pie.png")
    return _save_figure(fig, out_path)


def generate_monthly_category_chart() -> Optional[str]:
    """Generate pie chart for current month by category, save PNG, and return path or None."""
    today = datetime.date.today()
    start_month = today.replace(day=1)
    data = _fetch_category_sums(_iso(start_month), _iso(today))
    if not data:
        print("No data for monthly category chart.")
        return None

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
    ax.set_title("Monthly Expenses by Category")

    out_path = os.path.join(CHART_DIR, "monthly_category_pie.png")
    return _save_figure(fig, out_path)


def generate_time_series_chart(days: int = 30) -> Optional[str]:
    """Generate bar chart of daily totals for last `days` days and return saved path."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days - 1)
    rows = _fetch_daily_totals(_iso(start), _iso(today))
    if not rows:
        print("No data for time-series chart.")
        return None

    dates = [datetime.datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows]
    totals = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(dates, totals)
    ax.set_title(f"Daily Expenses — Last {days} days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Amount (₹)")
    fig.autofmt_xdate(rotation=45)

    out_path = os.path.join(CHART_DIR, f"timeseries_{days}d.png")
    return _save_figure(fig, out_path)


# --- convenience function for frontend/main integration ------------------

def generate_all_charts() -> dict:
    """Generate weekly, monthly and 30-day time-series charts. Return dict of {name: path}.
    If a chart couldn't be generated (no data), value will be None.
    """
    results = {
        "weekly_category": None,
        "monthly_category": None,
        "timeseries_30d": None,
    }

    results["weekly_category"] = generate_weekly_category_chart()
    results["monthly_category"] = generate_monthly_category_chart()
    results["timeseries_30d"] = generate_time_series_chart(30)

    return results


def ensure_chart_dir() -> None:
    os.makedirs(CHART_DIR, exist_ok=True)


# --- quick CLI helper ----------------------------------------------------

if __name__ == "__main__":
    print("visual_module_updated — generate charts and text summaries")
    ensure_chart_dir()
    print("\n" + get_weekly_summary_text())
    weekly = generate_weekly_category_chart()
    if weekly:
        print(f"Saved weekly chart: {weekly}")

    print("\n" + get_monthly_summary_text())
    monthly = generate_monthly_category_chart()
    if monthly:
        print(f"Saved monthly chart: {monthly}")

    ts = generate_time_series_chart(30)
    if ts:
        print(f"Saved time-series chart: {ts}")
