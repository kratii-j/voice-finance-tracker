import sqlite3
import datetime

def create_connection(db_name="expenses.db"):
    conn = sqlite3.connect(db_name)
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()

def add_expense(amount, category, date=None):
    if date is None:
        date = datetime.date.today().isoformat()
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amount, category, date))
    conn.commit()
    conn.close()
    # Optionally remove or comment out the next line after testing
    print(f"Added expense: {amount} to {category} on {date}")

def get_total_today():
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

def get_total_by_category(category):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE category = ?", (category,))
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)
    conn.close()
    print("Database and table created successfully.")
