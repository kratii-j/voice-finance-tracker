# main.py

from typing import List

from voice_module import (
    confirm_amount_flow,
    get_voice_input,
    parse_expense,
    repeat_last_transcript,
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
    # Setup DB
    create_table()

    speak("Voice tracker ready. Say a command or stop to quit.")
    MAX_ATTEMPTS = 5
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        user_text = get_voice_input(duration=5)

        if not user_text:
            attempts += 1
            print(f"No input. Attempt {attempts}/{MAX_ATTEMPTS}.")
            continue

        attempts = 0
        command = parse_expense(user_text)
        action = command.get("action", "unknown")

        if action == "exit":
            respond("info", "Goodbye. Stopping the tracker.")
            break

        if action == "help":
            show_help()
            continue

        if action == "repeat":
            previous = repeat_last_transcript()
            if previous:
                respond("repeat", f"You last said: {previous}")
            else:
                respond("repeat", "No previous command available.")
            continue

        if action == "add":
            amount = command.get("amount")
            category = command.get("category", "uncategorized")
            if amount is None:
                amount = confirm_amount_flow()
            if amount is None:
                respond("error", "Amount still missing. Expense not added.")
                continue
            expense_id = add_expense(amount, category)
            respond("add", f"Added ₹{amount} to {category}. Entry number {expense_id}.")
            continue

        if action == "balance":
            total = get_total_today()
            respond("balance", f"Today's total spend is ₹{total:.2f}.")
            continue

        if action == "recent":
            recent = get_recent_expenses(5)
            _speak_recent(recent)
            continue

        if action == "weekly":
            summary = get_weekly_summary_text()
            respond("weekly", summary)
            continue

        if action == "monthly":
            summary = get_monthly_summary_text()
            respond("monthly", summary)
            continue

        if action == "delete":
            removed = delete_last_expense()
            if removed:
                respond("delete", f"Deleted expense number {removed}.")
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
