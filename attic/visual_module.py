import sqlite3
import matplotlib.pyplot as plt
import datetime

DB_NAME = "expenses.db"

def fetch_all_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount FROM expenses")
    data = cursor.fetchall()
    conn.close()
    return data

def plot_expenses_by_category():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("No data available for plotting.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(7, 5))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expenses by Category")
    plt.show()

def plot_expenses_over_time():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("No data available for plotting.")
        return

    dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d") for row in data]
    totals = [row[1] for row in data]

    plt.figure(figsize=(8, 5))
    plt.bar(dates, totals, color='skyblue')
    plt.title("Expenses Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Amount (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("1️⃣ Plot by category\n2️⃣ Plot over time")
    choice = input("Choose option (1 or 2): ").strip()
    if choice == "1":
        plot_expenses_by_category()
    elif choice == "2":
        plot_expenses_over_time()
    else:
        print("Invalid choice.")
