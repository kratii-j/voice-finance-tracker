import os
import sqlite3
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from config import CHART_DIR, DB_NAME, DATE_FORMAT
from logger import log_error

def ensure_chart_dir() -> str:
    os.makedirs(CHART_DIR, exist_ok=True)
    return CHART_DIR

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    try:
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df
    except sqlite3.Error as exc:
        log_error("Data fetch error: %s", exc)
        raise

def plot_category_pie(df: pd.DataFrame, filename: str) -> Optional[str]:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(df["total"], labels=df["category"], autopct="%1.1f%%", startangle=140)
    ax.set_title("Spending by Category")
    path = os.path.join(ensure_chart_dir(), filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path

def plot_daily_bar(df: pd.DataFrame, filename: str) -> Optional[str]:
    if df.empty:
        return None
    df = df.sort_values("date")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["date"], df["total"], color="#4e79a7")
    ax.set_title("Daily Spending")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    ax.tick_params(axis="x", rotation=45)
    path = os.path.join(ensure_chart_dir(), filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path

def get_category_breakdown() -> pd.DataFrame:
    return fetch_dataframe(
        """
        SELECT category, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
        """
    )

def get_recent_daily_totals(days: int = 7) -> pd.DataFrame:
    query = """
        SELECT date, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE date >= date('now', ?)
        GROUP BY date
        ORDER BY date
    """
    offset = f"-{days - 1} day"
    return fetch_dataframe(query, (offset,))

def generate_all_charts() -> Dict[str, Optional[str]]:
    charts: Dict[str, Optional[str]] = {
        "category": plot_category_pie(get_category_breakdown(), "category_pie.png"),
        "daily": plot_daily_bar(get_recent_daily_totals(7), "daily_bar.png"),
    }
    return charts

def get_weekly_summary_text() -> str:
    df = get_recent_daily_totals(7)
    total = df["total"].sum() if not df.empty else 0
    avg = total / len(df) if not df.empty else 0
    return f"Weekly spend ₹{total:.2f} (daily avg ₹{avg:.2f})"

def get_monthly_summary_text() -> str:
    df = fetch_dataframe(
        """
        SELECT substr(date, 1, 7) AS month, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month DESC
        LIMIT 1
        """
    )
    if df.empty:
        return "No monthly data yet."
    row = df.iloc[0]
    return f"{row['month']} total ₹{row['total']:.2f}"
