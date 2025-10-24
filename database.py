import sqlite3
import datetime

DB_NAME = "expenses.db"

def create_connection(db_name=DB_NAME):
    return sqlite3.connect(db_name)

def create_table():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                time TEXT,
                payment_method TEXT
            )
        ''')
        conn.commit()

def add_expense(amount, category, date=None, description=None, time=None, payment_method=None):
    if date is None:
        date = datetime.date.today().isoformat()
    if time is None:
        time = datetime.datetime.now().strftime("%H:%M:%S")
    with create_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO expenses (amount, category, date, description, time, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (amount, category, date, description, time, payment_method))
        conn.commit()
    print(f"Added expense: {amount} to {category} on {date} {time}")

def get_total_today():
    today = datetime.date.today().isoformat()
    with create_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (today,))
        result = c.fetchone()[0]
    return result if result else 0

def get_total_by_category(category):
    with create_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT SUM(amount) FROM expenses WHERE category = ?", (category,))
        result = c.fetchone()[0]
    return result if result else 0

def get_recent_expenses(n=5):
    with create_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM expenses ORDER BY date DESC, time DESC LIMIT ?", (n,))
        rows = c.fetchall()
    return rows

def delete_expense(expense_id):
    with create_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

def update_expense(expense_id, amount=None, category=None, description=None, payment_method=None):
    updates = []
    params = []
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if payment_method is not None:
        updates.append("payment_method = ?")
        params.append(payment_method)
    if not updates:
        return  
    params.append(expense_id)
    sql = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
    with create_connection() as conn:
        c = conn.cursor()
        c.execute(sql, params)
        conn.commit()

def get_weekly_summary():
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    with create_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT category, SUM(amount) FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
        ''', (week_ago.isoformat(), today.isoformat()))
        return c.fetchall()

def get_monthly_summary():
    today = datetime.date.today()
    month_start = today.replace(day=1)
    with create_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT category, SUM(amount) FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
        ''', (month_start.isoformat(), today.isoformat()))
        return c.fetchall()

if __name__ == "__main__":
    create_table()
    print("Database ready with full schema and functions!")
