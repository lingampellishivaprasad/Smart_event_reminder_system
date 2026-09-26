# Smart Event Reminder System

A Python command-line application for creating and managing events and receiving local reminder notifications.

> **GitHub-safe version:** This version intentionally contains **no email sending, email addresses, passwords, API keys, personal contact details, or external services**.

## Features

- User registration and login
- Password hashing with PBKDF2-HMAC-SHA256
- Add events
- View events
- Search events by name
- Update events
- Delete events
- Configure reminder offsets in minutes
- Check reminders manually
- Run a continuous reminder monitor
- JSON-based local data storage
- Application logging
- Command-line arguments

## Requirements

- Python 3.9 or newer
- No third-party Python packages

All imports used by the project are from the Python standard library.

## Project Structure

```text
smart-event-reminder-system/
├── smart_event_reminder.py
├── README.md
├── requirements.txt
└── .gitignore
```

The following files are created while the program runs and are intentionally ignored by Git:

```text
smart_event_reminder_data.json
smart_event_reminder.log
```

## Run the Project

Clone or download the repository, then open a terminal in the project folder.

```bash
python smart_event_reminder.py
```

On systems where Python 3 is invoked as `python3`:

```bash
python3 smart_event_reminder.py
```

## Main Menu

```text
1. Register
2. Login
3. Exit
```

After login:

```text
1. Add Event
2. View Events
3. Search Events by Name
4. Update Event
5. Delete Event
6. Check Reminders
7. Run Reminder Monitor
8. Logout
```

## Event Date Format

Use:

```text
YYYY-MM-DD HH:MM
```

Example:

```text
2026-10-15 18:30
```

Reminder offsets are entered as comma-separated minutes:

```text
60,30,10
```

This represents reminders 60, 30, and 10 minutes before the event.

## Command-Line Modes

Check reminders once:

```bash
python smart_event_reminder.py --check-reminders
```

Run continuous monitoring:

```bash
python smart_event_reminder.py --monitor
```

Press `Ctrl+C` to stop continuous monitoring.

## Security Notes

The project stores users and events in a local JSON file.

Passwords are not stored as plain text. A random salt and PBKDF2-HMAC-SHA256 are used for password hashing.

For a real production application, use a proper database, stronger application-level security controls, access controls, backups, and a secrets-management solution.

## Privacy

This GitHub-safe version does not collect or send:

- Email addresses
- Phone numbers
- Personal contact information
- Gmail credentials
- API keys
- SMTP credentials

Do not commit real personal data or generated user data to the repository.

## GitHub Upload Checklist

Before uploading:

1. Open `smart_event_reminder.py`.
2. Confirm there are no real passwords, email addresses, API keys, or personal details.
3. Confirm `.gitignore` exists.
4. Confirm `smart_event_reminder_data.json` is not tracked.
5. Confirm `smart_event_reminder.log` is not tracked.
6. Upload only the project source and documentation.

Recommended repository contents:

```text
smart_event_reminder.py
README.md
requirements.txt
.gitignore
```

## Future Improvements

Possible future additions include:

- GUI interface
- Database storage
- Recurring events
- Event categories
- Calendar integration
- Notification history
- Unit tests
- Web interface

