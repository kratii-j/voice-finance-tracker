from database import add_expense, get_total_today
from visual_module_updated import (
    get_weekly_summary_text,
    get_monthly_summary_text,
    generate_all_charts,
    ensure_chart_dir,
)
from logger import log_info, log_error
import sys

ensure_chart_dir()

def demo_add_expense(amount, category):
    """Add expense and log the action."""
    try:
        add_expense(amount, category)
        log_info(f"Expense added: ₹{amount} to {category}")
        total_today = get_total_today()
        print(f"Added ₹{amount} to {category}. Total spent today: ₹{total_today}")
    except Exception as e:
        log_error(f"Failed to add expense: {e}")
        print(f"Error adding expense: {e}")

def demo_generate_summaries_and_charts():
    """Generate text summaries and charts, log progress."""
    try:
        weekly_text = get_weekly_summary_text()
        monthly_text = get_monthly_summary_text()
        print("\n--- Weekly Summary ---")
        print(weekly_text)
        print("\n--- Monthly Summary ---")
        print(monthly_text)

        charts = generate_all_charts()
        for key, path in charts.items():
            if path:
                log_info(f"{key} chart generated at {path}")
                print(f"{key} chart saved: {path}")
    except Exception as e:
        log_error(f"Failed to generate summaries/charts: {e}")
        print(f"Error generating summaries/charts: {e}")

if __name__ == "__main__":
    print("Integration Demo Started\n")
    
    demo_add_expense(250, "food")
    demo_add_expense(100, "transport")
    
    demo_generate_summaries_and_charts()
    
    print("\nIntegration Demo Completed")
