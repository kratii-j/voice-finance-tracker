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

import sqlite3, datetime, matplotlib.pyplot as plt, os

DB_NAME = "expenses.db"

def generate_weekly_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=7)
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE date >= ? GROUP BY category",
        (week_start.isoformat(),),
    )
    data = cursor.fetchall()
    conn.close()

    if not data:
        return ("No data for this week", None)

    categories = [d[0] for d in data]
    totals = [d[1] for d in data]

    os.makedirs("static/charts", exist_ok=True)
    chart_path = os.path.join("static", "charts", "weekly_category_pie.png")

    plt.figure(figsize=(6, 5))
    plt.pie(totals, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title(f"Weekly Spending ({week_start} to {today})")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    text_summary = (
        f"Weekly Summary ({week_start} to {today}):\n"
        + "\n".join([f" - {cat}: ₹{amt:.2f}" for cat, amt in data])
    )

    return text_summary, chart_path


def generate_monthly_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.date.today()
    month_start = today.replace(day=1)
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE date >= ? GROUP BY category",
        (month_start.isoformat(),),
    )
    data = cursor.fetchall()
    conn.close()

    if not data:
        return ("No data for this month", None, None)

    categories = [d[0] for d in data]
    totals = [d[1] for d in data]

    os.makedirs("static/charts", exist_ok=True)
    monthly_chart = os.path.join("static", "charts", "monthly_category_pie.png")
    plt.figure(figsize=(6, 5))
    plt.pie(totals, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title(f"Monthly Spending ({today.strftime('%B %Y')})")
    plt.tight_layout()
    plt.savefig(monthly_chart)
    plt.close()

    # time series chart for last 30 days
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    thirty_days_ago = today - datetime.timedelta(days=30)
    cursor.execute(
        "SELECT date, SUM(amount) FROM expenses WHERE date >= ? GROUP BY date ORDER BY date",
        (thirty_days_ago.isoformat(),),
    )
    time_data = cursor.fetchall()
    conn.close()

    timeseries_chart = os.path.join("static", "charts", "timeseries_30d.png")
    if time_data:
        dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d") for d in time_data]
        amounts = [d[1] for d in time_data]
        plt.figure(figsize=(8, 4))
        plt.plot(dates, amounts, marker="o", color="teal")
        plt.title("Spending in Last 30 Days")
        plt.xlabel("Date")
        plt.ylabel("Amount (₹)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(timeseries_chart)
        plt.close()

    text_summary = (
        f"Monthly Summary ({today.strftime('%B %Y')}):\n"
        + "\n".join([f" - {cat}: ₹{amt:.2f}" for cat, amt in data])
    )

    return text_summary, monthly_chart, timeseries_chart
