# main.py

from voice_module import get_voice_input, speak, add_expense_nlp
from database import (
    create_connection,
    create_table,
    add_expense,
    get_total_today,
    get_total_by_category,
)
import sys


def main():
    # Setup DB
    conn = create_connection()
    create_table(conn)
    conn.close()

    speak("Voice expense tracker started. Say a command or say stop to quit.")

    MAX_ATTEMPTS = 5
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        user_text = get_voice_input(duration=5)

        if not user_text:
            attempts += 1
            print(f"No input detected. Attempt {attempts} of {MAX_ATTEMPTS}")
            continue

        attempts = 0

        # Exit commands
        if any(cmd in user_text for cmd in ["stop", "exit", "quit"]):
            speak("Stopping the expense tracker. Goodbye.")
            print("Exiting...")
            sys.exit(0)

        # Add expense
        amount, category = add_expense_nlp(user_text)
        if amount:
            add_expense(amount, category.lower())  # normalize category
            speak(f"Added {amount} rupees to {category}")
            print(f"Expense added: {amount} -> {category}")
            continue

        # Show today's total
        if "balance" in user_text or "today" in user_text:
            total = get_total_today()
            speak(f"Your total spending today is {total} rupees")
            print(f"Today's total: {total}")
            continue

        # Show total by category
        if "total on" in user_text or "spent on" in user_text:
            words = user_text.split()
            if "on" in words:
                idx = words.index("on")
                if idx + 1 < len(words):
                    category = words[idx + 1].lower()
                    total_cat = get_total_by_category(category)
                    speak(f"You have spent {total_cat} rupees on {category}")
                    print(f"Total on {category}: {total_cat}")
                    continue

        # Unknown command
        speak("Command not recognized. Try again or say help.")
        print("Unrecognized command.")

    if attempts >= MAX_ATTEMPTS:
        speak("No command received. Exiting the assistant.")
        print("No input received. Exiting...")


if __name__ == "__main__":
    main()
