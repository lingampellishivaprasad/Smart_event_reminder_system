"""
Smart Event Reminder System
A local command-line event manager with reminders.

No email, personal data, or external services are used.
Data is stored locally in smart_event_reminder_data.json.
"""

import argparse
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timedelta

DATA_FILE = "smart_event_reminder_data.json"
LOG_FILE = "smart_event_reminder.log"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
CHECK_INTERVAL_SECONDS = 30
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def default_data():
    return {"users": [], "events": [], "next_user_id": 1, "next_event_id": 1}


def ensure_schema(data):
    if not isinstance(data, dict):
        return default_data()
    data.setdefault("users", [])
    data.setdefault("events", [])
    data.setdefault("next_user_id", 1)
    data.setdefault("next_event_id", 1)
    if not isinstance(data["users"], list):
        data["users"] = []
    if not isinstance(data["events"], list):
        data["events"] = []
    return data


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return ensure_schema(json.load(file))
    except (OSError, json.JSONDecodeError) as error:
        logging.error("Failed to load data: %s", error)
        return default_data()


def save_data(data):
    try:
        temporary_file = DATA_FILE + ".tmp"
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        os.replace(temporary_file, DATA_FILE)
        return True
    except OSError as error:
        logging.error("Failed to save data: %s", error)
        return False


def validate_email(email):
    """Retained as a generic validation helper; no email is stored or sent."""
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def parse_datetime(value):
    return datetime.strptime(value.strip(), DATETIME_FORMAT)


def format_datetime(value):
    return value.strftime(DATETIME_FORMAT)


def parse_offsets(value):
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        raise ValueError("Enter at least one reminder offset.")
    offsets = []
    for part in parts:
        if not part.isdigit():
            raise ValueError("Reminder offsets must be whole numbers.")
        minutes = int(part)
        if minutes < 0:
            raise ValueError("Reminder offsets cannot be negative.")
        offsets.append(minutes)
    return sorted(set(offsets), reverse=True)


def hash_password(password, salt_hex=None):
    salt = secrets.token_bytes(16) if salt_hex is None else bytes.fromhex(salt_hex)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100_000
    )
    return salt.hex(), password_hash.hex()


def verify_password(password, salt_hex, stored_hash_hex):
    _, test_hash = hash_password(password, salt_hex)
    return hmac.compare_digest(test_hash, stored_hash_hex)


def find_user_by_username(data, username):
    username = username.strip().lower()
    return next(
        (user for user in data["users"] if user["username"].lower() == username),
        None,
    )


def find_events_by_owner(data, username):
    username = username.strip().lower()
    return [event for event in data["events"]
            if event["owner"].lower() == username]


def find_event_by_id(data, event_id, username=None):
    for event in data["events"]:
        if event["id"] != event_id:
            continue
        if username is None or event["owner"].lower() == username.strip().lower():
            return event
    return None


def register_user(data):
    print("\n=== Register ===")
    username = input("Username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    if find_user_by_username(data, username):
        print("Username already exists.")
        return

    password = input("Password (minimum 6 characters): ")
    if len(password) < 6:
        print("Password must contain at least 6 characters.")
        return

    salt, password_hash = hash_password(password)
    data["users"].append({
        "id": data["next_user_id"],
        "username": username,
        "salt": salt,
        "password_hash": password_hash,
    })
    data["next_user_id"] += 1
    save_data(data)
    print("Registration successful.")


def login_user(data):
    print("\n=== Login ===")
    username = input("Username: ").strip()
    password = input("Password: ")

    user = find_user_by_username(data, username)
    if not user or not verify_password(
        password, user["salt"], user["password_hash"]
    ):
        print("Invalid username or password.")
        return None

    print(f"Welcome, {user['username']}!")
    return user["username"]


def add_event(data, username):
    print("\n=== Add Event ===")
    title = input("Event name: ").strip()
    if not title:
        print("Event name cannot be empty.")
        return

    description = input("Description: ").strip()
    date_text = input(f"Date and time ({DATETIME_FORMAT}): ").strip()

    try:
        event_time = parse_datetime(date_text)
        offsets = parse_offsets(
            input("Reminder offsets in minutes (e.g. 60,30,10): ")
        )
    except ValueError as error:
        print(f"Invalid input: {error}")
        return

    event = {
        "id": data["next_event_id"],
        "owner": username,
        "title": title,
        "description": description,
        "datetime": format_datetime(event_time),
        "reminder_offsets": offsets,
        "sent_reminders": [],
        "created_at": format_datetime(datetime.now()),
    }

    data["events"].append(event)
    data["next_event_id"] += 1
    save_data(data)
    print(f"Event #{event['id']} added successfully.")


def view_events(data, username):
    events = find_events_by_owner(data, username)
    events.sort(key=lambda event: event["datetime"])

    print("\n=== Your Events ===")
    if not events:
        print("No events found.")
        return

    for event in events:
        print(f"\nID: {event['id']}")
        print(f"Name: {event['title']}")
        print(f"Description: {event['description'] or '-'}")
        print(f"Date/time: {event['datetime']}")
        print(f"Reminders: {', '.join(map(str, event['reminder_offsets']))} minutes")


def search_events(data, username):
    query = input("Search event name: ").strip().lower()
    events = [
        event for event in find_events_by_owner(data, username)
        if query in event["title"].lower()
    ]

    if not events:
        print("No matching events found.")
        return

    for event in events:
        print(f"#{event['id']} - {event['title']} - {event['datetime']}")


def update_event(data, username):
    try:
        event_id = int(input("Event ID: "))
    except ValueError:
        print("Invalid event ID.")
        return

    event = find_event_by_id(data, event_id, username)
    if not event:
        print("Event not found.")
        return

    print("Press Enter to keep the existing value.")
    title = input(f"Event name [{event['title']}]: ").strip()
    description = input(
        f"Description [{event['description']}]: "
    ).strip()
    date_text = input(
        f"Date/time [{event['datetime']}]: "
    ).strip()
    offsets_text = input(
        f"Reminder offsets [{','.join(map(str, event['reminder_offsets']))}]: "
    ).strip()

    try:
        if title:
            event["title"] = title
        if description:
            event["description"] = description
        if date_text:
            event["datetime"] = format_datetime(parse_datetime(date_text))
        if offsets_text:
            event["reminder_offsets"] = parse_offsets(offsets_text)
        event["sent_reminders"] = []
    except ValueError as error:
        print(f"Invalid input: {error}")
        return

    save_data(data)
    print("Event updated successfully.")


def delete_event(data, username):
    try:
        event_id = int(input("Event ID: "))
    except ValueError:
        print("Invalid event ID.")
        return

    event = find_event_by_id(data, event_id, username)
    if not event:
        print("Event not found.")
        return

    data["events"].remove(event)
    save_data(data)
    print("Event deleted successfully.")


def check_reminders(data, username=None):
    now = datetime.now()
    triggered = []

    for event in data["events"]:
        if username and event["owner"].lower() != username.lower():
            continue

        try:
            event_time = parse_datetime(event["datetime"])
        except ValueError:
            logging.warning("Invalid datetime in event %s", event.get("id"))
            continue

        if event_time < now - timedelta(minutes=1):
            continue

        sent = set(event.get("sent_reminders", []))

        for offset in event["reminder_offsets"]:
            reminder_time = event_time - timedelta(minutes=offset)
            reminder_key = str(offset)

            if reminder_key in sent:
                continue

            if reminder_time <= now <= reminder_time + timedelta(seconds=60):
                message = (
                    f"REMINDER: '{event['title']}' starts at "
                    f"{event['datetime']} ({offset} minutes from now)."
                )
                print(message)
                logging.info(message)
                event.setdefault("sent_reminders", []).append(offset)
                triggered.append(event["id"])

    if triggered:
        save_data(data)

    return triggered


def reminder_monitor(data, username):
    print("\nReminder monitor started.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            check_reminders(data, username)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nReminder monitor stopped.")


def user_menu(data, username):
    while True:
        print(
            "\n=== Event Reminder Menu ===\n"
            "1. Add Event\n"
            "2. View Events\n"
            "3. Search Events by Name\n"
            "4. Update Event\n"
            "5. Delete Event\n"
            "6. Check Reminders\n"
            "7. Run Reminder Monitor\n"
            "8. Logout"
        )

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_event(data, username)
        elif choice == "2":
            view_events(data, username)
        elif choice == "3":
            search_events(data, username)
        elif choice == "4":
            update_event(data, username)
        elif choice == "5":
            delete_event(data, username)
        elif choice == "6":
            check_reminders(data, username)
        elif choice == "7":
            reminder_monitor(data, username)
        elif choice == "8":
            print("Logged out.")
            return
        else:
            print("Invalid option.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smart Event Reminder System"
    )
    parser.add_argument(
        "--check-reminders",
        action="store_true",
        help="Check all stored reminders once.",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Continuously monitor all stored reminders.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data = load_data()

    if args.check_reminders:
        check_reminders(data)
        return

    if args.monitor:
        try:
            while True:
                check_reminders(data)
                time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")
        return

    while True:
        print(
            "\n=== Smart Event Reminder System ===\n"
            "1. Register\n"
            "2. Login\n"
            "3. Exit"
        )

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user(data)
        elif choice == "2":
            username = login_user(data)
            if username:
                user_menu(data, username)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
