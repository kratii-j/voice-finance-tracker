import sqlite3
import datetime

DB_NAME = "expenses.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_total_expenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def get_monthly_total(year=None, month=None):
    if year is None or month is None:
        today = datetime.date.today()
        year, month = today.year, today.month
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y', date)=? AND strftime('%m', date)=?", 
                (str(year), f"{month:02d}"))
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def get_expenses_by_category():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cur.fetchall()
    conn.close()
    return data

def get_daily_average():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date")
    results = cur.fetchall()
    conn.close()
    if not results:
        return 0
    total_spent = sum(amount for _, amount in results)
    return total_spent / len(results)
import os
import matplotlib.pyplot as plt

def get_weekly_summary_text():
    """Generate a weekly expense summary (last 7 days)."""
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)
    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category",
                (week_ago.isoformat(), today.isoformat()))
    data = cur.fetchall()
    conn.close()

    if not data:
        return "No expenses recorded this week."

    text_summary = "Weekly Summary (last 7 days):\n"
    total = 0
    for category, amount in data:
        text_summary += f"  {category}: ₹{amount:.2f}\n"
        total += amount
    text_summary += f"Total Spent This Week: ₹{total:.2f}"
    return text_summary


def get_monthly_summary_text():
    """Generate a monthly expense summary (current month)."""
    today = datetime.date.today()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=? GROUP BY category",
                (f"{today.year}-{today.month:02d}",))
    data = cur.fetchall()
    conn.close()

    if not data:
        return "No expenses recorded this month."

    text_summary = f"Monthly Summary ({today.strftime('%B %Y')}):\n"
    total = 0
    for category, amount in data:
        text_summary += f"  {category}: ₹{amount:.2f}\n"
        total += amount
    text_summary += f"Total Spent This Month: ₹{total:.2f}"
    return text_summary


def generate_summary_chart(period="weekly"):
    """Generate a pie chart summary for weekly or monthly expenses."""
    os.makedirs("static/charts", exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.date.today()

    if period == "weekly":
        week_ago = today - datetime.timedelta(days=7)
        cur.execute("SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category",
                    (week_ago.isoformat(), today.isoformat()))
        chart_path = "static/charts/weekly_summary_chart.png"
    else:
        cur.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=? GROUP BY category",
                    (f"{today.year}-{today.month:02d}",))
        chart_path = "static/charts/monthly_summary_chart.png"

    data = cur.fetchall()
    conn.close()

    if not data:
        print(f"No data available for {period} summary chart.")
        return

    categories, amounts = zip(*data)
    plt.figure(figsize=(5, 5))
    plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title(f"{period.capitalize()} Expense Summary")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    print(f"Chart saved at {chart_path}")
if __name__ == "__main__":
    print("📊 Expense Summary:")
    print(f"Total Expenses: ₹{get_total_expenses():.2f}")
    print(f"Total This Month: ₹{get_monthly_total():.2f}")
    print(f"Average Daily Spending: ₹{get_daily_average():.2f}")
    print("Category-wise Breakdown:")
    for category, total in get_expenses_by_category():
        print(f"  {category}: ₹{total:.2f}")

    print("\n🗓️ Weekly Summary:")
    print(get_weekly_summary_text())

    print("\n🗓️ Monthly Summary:")
    print(get_monthly_summary_text())

    print("\n📈 Generating charts...")
    generate_summary_chart("weekly")
    generate_summary_chart("monthly")
