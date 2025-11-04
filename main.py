# main.py

from datetime import datetime
from typing import Dict, List, Optional

from budget_module import (
    evaluate_monthly_budgets,
    get_alert_for_category,
)
from config import DATE_FORMAT

from voice_module import (
    confirm_amount_flow,
    get_voice_input,
    parse_expense,
    respond,
    speak,
)
from database import (
    add_expense,
    create_table,
    delete_last_expense,
    get_recent_expenses,
    get_total_today,
)
from summary_module import get_monthly_summary_text, get_weekly_summary_text


def show_help() -> str:
    help_text = (
        "Try commands like:\n"
        "- Add 200 to food\n"
        "- What's my balance today\n"
        "- Show recent expenses\n"
        "- Give weekly summary\n"
        "- Delete last expense\n"
        "- Repeat last command\n"
        "- Stop to exit"
    )
    print(help_text)
    speak(
        "You can add expenses, ask for balance, recent items, weekly or monthly summary, delete last expense, or say stop.",
        tone="info",
    )
    return help_text


def _speak_recent(items: List[dict]) -> None:
    if not items:
        respond("recent", "No recent expenses recorded.")
        return
    top = items[0]
    respond(
        "recent",
        f"Most recent is ₹{top['amount']} on {top['category']} dated {top['date']} at {top['time']}.",
    )


def main() -> None:
    # ensure DB schema exists
    create_table()

    speak("Voice tracker ready. Say a command or stop to quit.")
    MAX_ATTEMPTS = 5
    attempts = 0

    previous_command: Optional[Dict] = None
    while attempts < MAX_ATTEMPTS:
        user_text = get_voice_input(duration=5)

        if not user_text:
            attempts += 1
            print(f"No input. Attempt {attempts}/{MAX_ATTEMPTS}.")
            continue

        attempts = 0
        command = parse_expense(user_text)
        action = command.get("action", "unknown")

        # If user asked to repeat, replace current command with the last executed one
        if action == "repeat":
            if previous_command:
                respond("info", "Repeating the last command.")
                # reuse previous_command (do not overwrite previous_command yet)
                command = previous_command.copy()
                action = command.get("action", "unknown")
            else:
                respond("repeat", "No previous command available.")
                continue

        # Handle actions
        if action == "exit":
            respond("info", "Goodbye. Stopping the tracker.")
            break

        if action == "help":
            show_help()
            # do not record help as previous actionable command
            continue

        if action == "add":
            amount = command.get("amount")
            category = command.get("category", "uncategorized")
            expense_date = command.get("date")
            description = command.get("description")
            # slot filling for amount
            if amount is None:
                amount = confirm_amount_flow()
                if amount is None:
                    respond("error", "Amount still missing. Expense not added.")
                    continue
            try:
                expense_id = add_expense(amount, category, date=expense_date, description=description)
                respond("add", f"Added ₹{amount} to {category}. Entry number {expense_id}.")
                # record this successful command for potential repeat
                previous_command = {"action": "add", "amount": amount, "category": category}
                alert_year: Optional[int] = None
                alert_month: Optional[int] = None
                if expense_date:
                    try:
                        parsed = datetime.strptime(expense_date, DATE_FORMAT)
                        alert_year, alert_month = parsed.year, parsed.month
                    except ValueError:
                        pass
                budget_status = get_alert_for_category(category, year=alert_year, month=alert_month)
                if budget_status:
                    tone = "error" if budget_status.level == "critical" else "info"
                    speak(budget_status.message, tone=tone)
            except Exception as exc:
                respond("error", "Failed to add the expense.")
            continue

        if action == "balance":
            total = get_total_today()
            respond("balance", f"Today's total spend is ₹{total:.2f}.")
            previous_command = {"action": "balance"}
            continue

        if action == "recent":
            recent = get_recent_expenses(5)
            _speak_recent(recent)
            previous_command = {"action": "recent"}
            continue

        if action == "weekly":
            summary = get_weekly_summary_text()
            respond("weekly", summary)
            previous_command = {"action": "weekly"}
            continue

        if action == "monthly":
            summary = get_monthly_summary_text()
            respond("monthly", summary)
            for status in evaluate_monthly_budgets():
                if status.level == "warning":
                    speak(status.message, tone="info")
                elif status.level == "critical":
                    speak(status.message, tone="error")
            previous_command = {"action": "monthly"}
            continue

        if action == "delete":
            removed = delete_last_expense()
            if removed:
                respond("delete", f"Deleted expense number {removed}.")
                previous_command = {"action": "delete"}
            else:
                respond("delete", "No expense to delete.")
            continue

        if action == "unknown":
            respond(
                "error",
                "I did not recognise that. Say help for a list of commands.",
            )
            attempts += 1
            continue

    if attempts >= MAX_ATTEMPTS:
        respond("error", "No command detected repeatedly. Exiting.")


if __name__ == "__main__":
    main()
