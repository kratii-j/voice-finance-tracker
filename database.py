import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

from config import DB_NAME, DATE_FORMAT
from logger import log_error, log_info

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    payment_method TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

def create_connection(db_name: str = DB_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def create_table() -> None:
    try:
        with create_connection() as conn:
            conn.execute(SCHEMA)
            conn.commit()
        log_info("Database schema ensured.")
    except sqlite3.Error as exc:
        log_error("Failed to create schema: %s", exc)
        raise

def _normalize_date(date: Optional[str] = None) -> str:
    if date:
        return date
    return datetime.now().strftime(DATE_FORMAT)

def _normalize_time(time_str: Optional[str] = None) -> str:
    if time_str:
        return time_str
    return datetime.now().strftime("%H:%M:%S")

def add_expense(
    amount: float,
    category: str,
    date: Optional[str] = None,
    description: Optional[str] = None,
    time: Optional[str] = None,
    payment_method: Optional[str] = None,
) -> int:
    payload = {
        "amount": amount,
        "category": category,
        "description": description,
        "payment_method": payment_method,
        "date": _normalize_date(date),
        "time": _normalize_time(time),
    }
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO expenses (amount, category, description, payment_method, date, time)
                VALUES (:amount, :category, :description, :payment_method, :date, :time)
                """,
                payload,
            )
            conn.commit()
            expense_id = cur.lastrowid
        log_info("Inserted expense %s -> %s", expense_id, payload)
        return expense_id
    except sqlite3.Error as exc:
        log_error("Failed to insert expense: %s", exc)
        raise

def get_total_today() -> float:
    today = _normalize_date()
    try:
        with create_connection() as conn:
            cur = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date = ?",
                (today,),
            )
            total = cur.fetchone()[0]
        return float(total or 0.0)
    except sqlite3.Error as exc:
        log_error("Failed to fetch today's total: %s", exc)
        raise

def get_total_by_category() -> List[Tuple[str, float]]:
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                SELECT category, COALESCE(SUM(amount), 0) AS total
                FROM expenses
                GROUP BY category
                ORDER BY total DESC
                """
            )
            results = [(row["category"], float(row["total"])) for row in cur.fetchall()]
        return results
    except sqlite3.Error as exc:
        log_error("Failed to fetch total by category: %s", exc)
        raise

def get_recent_expenses(limit: int = 5) -> List[Dict[str, Any]]:
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, amount, category, description, payment_method, date, time
                FROM expenses
                ORDER BY date DESC, time DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        log_error("Failed to fetch recent expenses: %s", exc)
        raise

def delete_last_expense() -> Optional[int]:
    try:
        with create_connection() as conn:
            cur = conn.execute(
                "SELECT id FROM expenses ORDER BY date DESC, time DESC, id DESC LIMIT 1"
            )
            row = cur.fetchone()
            if not row:
                return None
            expense_id = row["id"]
            conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
        log_info("Deleted last expense id=%s", expense_id)
        return expense_id
    except sqlite3.Error as exc:
        log_error("Failed to delete last expense: %s", exc)
        raise

def delete_expense(expense_id: int) -> bool:
    try:
        with create_connection() as conn:
            cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
        deleted = cur.rowcount > 0
        log_info("Delete expense id=%s -> %s", expense_id, deleted)
        return deleted
    except sqlite3.Error as exc:
        log_error("Failed to delete expense: %s", exc)
        raise

def update_expense(
    expense_id: int,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
) -> bool:
    fields: List[str] = []
    params: List[Any] = []

    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)
    if category:
        fields.append("category = ?")
        params.append(category)
    if description is not None:
        fields.append("description = ?")
        params.append(description)
    if payment_method is not None:
        fields.append("payment_method = ?")
        params.append(payment_method)
    if date:
        fields.append("date = ?")
        params.append(date)
    if time:
        fields.append("time = ?")
        params.append(time)

    if not fields:
        return False

    params.append(expense_id)

    sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"

    try:
        with create_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
        updated = cur.rowcount > 0
        log_info("Update expense id=%s -> %s", expense_id, updated)
        return updated
    except sqlite3.Error as exc:
        log_error("Failed to update expense: %s", exc)
        raise

def get_weekly_summary(weeks: int = 1) -> List[Dict[str, Any]]:
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                SELECT date, COALESCE(SUM(amount), 0) AS total
                FROM expenses
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date DESC
                """,
                (start_date.strftime(DATE_FORMAT), end_date.strftime(DATE_FORMAT)),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        log_error("Failed to fetch weekly summary: %s", exc)
        raise

def get_monthly_summary(year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                SELECT date, COALESCE(SUM(amount), 0) AS total
                FROM expenses
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date
                """,
                (start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT)),
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        log_error("Failed to fetch monthly summary: %s", exc)
        raise

def get_all_expenses() -> List[Dict[str, Any]]:
    try:
        with create_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, amount, category, description, payment_method, date, time
                FROM expenses
                ORDER BY date DESC, time DESC, id DESC
                """
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        log_error("Failed to fetch expenses: %s", exc)
        raise
