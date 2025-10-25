import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from config import DB_NAME, DATE_FORMAT
from logger import log_error

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def _fetch_single(query: str, params: Tuple = ()) -> float:
    try:
        with get_connection() as conn:
            cur = conn.execute(query, params)
            result = cur.fetchone()
            return float(result[0] or 0.0)
    except sqlite3.Error as exc:
        log_error("Summary fetch error: %s", exc)
        raise

def get_total_expenses() -> float:
    return _fetch_single("SELECT COALESCE(SUM(amount), 0) FROM expenses")

def get_monthly_total(year: Optional[int] = None, month: Optional[int] = None) -> float:
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return _fetch_single(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date >= ? AND date < ?",
        (start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT)),
    )

def get_expenses_by_category() -> List[Dict[str, float]]:
    try:
        with get_connection() as conn:
            cur = conn.execute(
                """
                SELECT category, COALESCE(SUM(amount), 0) AS total
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
                """
            )
            return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Category breakdown error: %s", exc)
        raise

def get_daily_totals(days: int = 7) -> List[Dict[str, float]]:
    start = datetime.now() - timedelta(days=days - 1)
    try:
        with get_connection() as conn:
            cur = conn.execute(
                """
                SELECT date, COALESCE(SUM(amount), 0) AS total
                FROM expenses
                WHERE date >= ?
                GROUP BY date
                ORDER BY date
                """,
                (start.strftime(DATE_FORMAT),),
            )
            return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        log_error("Daily totals error: %s", exc)
        raise

def get_weekly_summary_text() -> str:
    totals = get_daily_totals(days=7)
    total_amount = sum(row["total"] for row in totals)
    avg = total_amount / 7 if totals else 0
    top_categories = get_expenses_by_category()[:3]
    lines = [
        f"Weekly spend: ₹{total_amount:.2f}",
        f"Daily average: ₹{avg:.2f}",
    ]
    if top_categories:
        cats = ", ".join(f"{c['category']} (₹{c['total']:.0f})" for c in top_categories)
        lines.append(f"Top categories: {cats}")
    return "\n".join(lines)

def get_monthly_summary_text() -> str:
    now = datetime.now()
    total = get_monthly_total(now.year, now.month)
    cat_breakdown = get_expenses_by_category()
    lines = [f"{now.strftime('%B %Y')} total: ₹{total:.2f}"]
    if cat_breakdown:
        cats = ", ".join(f"{c['category']} (₹{c['total']:.0f})" for c in cat_breakdown[:5])
        lines.append(f"Leading categories: {cats}")
    return "\n".join(lines)
