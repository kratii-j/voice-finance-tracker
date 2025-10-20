# main.py

from voice_module import get_voice_input, speak, parse_expense
from database import (
    create_connection,
    create_table,
    add_expense,
    get_total_today,
    get_total_by_category,
)
import sys

def show_help():
    help_text = (
        "You can say things like:\n"
        "- 'Add 200 to food'\n"
        "- 'Show my balance'\n"
        "- 'Show recent expenses'\n"
        "- 'Give me weekly summary'\n"
        "- 'Delete last expense'\n"
        "- 'Stop' or 'Exit' to quit"
    )
    print(help_text)
    speak("Here are some things you can say: add expense, show balance, recent expenses, summary, or stop.")
    return help_text


def main():
    # Setup DB
    conn = create_connection()
    create_table(conn)
    conn.close()

    speak("Voice expense tracker started. Say a command or say stop to quit.")

    MAX_ATTEMPTS = 5
    attempts = 0

    try:
        while attempts < MAX_ATTEMPTS:
            user_text = get_voice_input(duration=5)

            if not user_text:
                attempts += 1
                print(f"No input detected. Attempt {attempts} of {MAX_ATTEMPTS}")
                continue

            attempts = 0

            cmd = parse_expense(user_text)
            action = cmd.get("action", "unknown")

            if action == "exit":
                speak("Goodbye! Closing the expense tracker")
                print("Exiting...")
                sys.exit(0)

            elif action == "add":
                amount = cmd.get("amount")
                category = cmd.get("category", "uncategorized")
                if amount is not None:
                    add_expense(amount, category)
                    speak(f"Added {amount} rupees to {category}", tone="success")
                    print(f"Added ₹{amount} -> {category}")
                else:
                    speak("Sorry! I didn't catch the amount. Please speak again.", tone="error")
                continue

            elif action == "balance":
                total = get_total_today()
                speak(f"Your total spendings today are {total}", tone="info")
                print(f"Today's total: {total}")
                continue

            elif action == "recent":
                # placeholder: database function for recent not implemented; add when ready
                speak("Showing recent transactions.", tone="info")
                print("Show recent transactions (not yet implemented).")
                continue

            elif action == "weekly" or action == "monthly":
                speak("Summary feature not implemented yet.", tone="summary")
                print(f"Requested {action} summary (not implemented).")
                continue

            elif action == "delete":
                # placeholder delete behavior
                speak("Delete feature is not implemented yet.", tone="error")
                print("Delete last expense (not implemented).")
                continue

            elif action == "help":
                show_help()
                continue

            else:
                attempts += 1
                speak("Command not recognized. Please say again", tone="error")
                print(f"User command: {user_text}. Attempt {attempts} of {MAX_ATTEMPTS}")
                continue

        if attempts >= MAX_ATTEMPTS:
            speak("No command received. Exiting the assistant.", tone="error")
            print("No input received. Exiting...")

    except KeyboardInterrupt:
        speak("Interrupted. Exiting the assistant.", tone="error")
        print("Interrupted by user. Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
