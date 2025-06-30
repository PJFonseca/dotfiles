import os
import csv
from datetime import datetime, timezone, timedelta
import caldav
from caldav.elements import dav
from getpass import getpass
import json

# Define constants
CSV_FILE = 'jira_export.csv'
SECRETS_FILE = os.path.expanduser('~/.secrets/jira2cal.secrets')
CALDAV_URL = 'https://fonzies.synology.me/caldav/pjfonseca'
CALENDAR_NAME = 'JIRA'

# Function to load credentials from a .secrets file
def load_credentials():
    secrets_dir = os.path.dirname(SECRETS_FILE)

    if os.path.isfile(secrets_dir):
        print(f"Error: {secrets_dir} exists and is a file, not a directory.")
        sys.exit(1)

    os.makedirs(secrets_dir, exist_ok=True)

    if os.path.exists(SECRETS_FILE):
        creds = {}
        with open(SECRETS_FILE, 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    creds[k.strip()] = v.strip()
        if 'username' in creds and 'password' in creds:
            return creds['username'], creds['password']

    username = input("Enter your Synology CalDAV username: ")
    password = getpass("Enter your CalDAV password: ")

    with open(SECRETS_FILE, 'w') as f:
        f.write(f"username={username}\npassword={password}\n")
    return username, password


# Function to get the start and end date of the current week
def get_current_week_dates():
    today = datetime.now(timezone.utc)
    start_of_week = today - timedelta(days=today.weekday())  # Start of the current week (Monday)
    end_of_week = start_of_week # timedelta(days=6) End of the current week (Sunday)
    return start_of_week, end_of_week

# Function to parse date from the CSV field (returns datetime object or None)
def parse_datetime(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string, '%d/%b/%y %I:%M %p')
        except ValueError:
            return None
    return None

# Function to create events from the CSV file and add them to the calendar
def create_events_from_csv(calendar):
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            issue_type = row.get('Issue Type', '').strip().lower()
            if issue_type not in ['task', 'sub-task']:
                continue  # Skip non-task/sub-task items

            status = row.get('Status', 'UNKNOWN')
            priority = row.get('Priority', 'No Priority')
            issue_key = row.get('Issue key', 'UNKNOWN')
            summary_raw = row.get('Summary', 'No Summary')
            description = row.get('Description', '')

            # Try to parse start and end dates
            start = parse_datetime(row.get('Custom field (Target start)'))
            end = parse_datetime(row.get('Custom field (Target end)'))

            if not start or not end:
                # If no dates, use current week as fallback
                start, end = get_current_week_dates()
                summary = f"DATES TBD - {status} - {priority} - {issue_key} - {summary_raw}"
                print(f"⏭ No dates found, using current week: {summary}")
            else:
                summary = f"{status} - {priority} - {issue_key} - {summary_raw}"

            # Create the event
            event_template = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//jira2cal//EN
BEGIN:VEVENT
UID:{issue_key}@jira2cal
DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{summary}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR
"""
            calendar.add_event(event_template)
            print(f"✅ Added: {summary}")

# Main function to run the script
def main():
    # Load credentials
    username, password = load_credentials()

    # Connect to the CalDAV server
    client = caldav.DAVClient(CALDAV_URL, username=username, password=password)
    principal = client.principal()

    # Find the specified calendar
    calendars = principal.calendars()
    calendar = None
    for cal in calendars:
        if cal.name == CALENDAR_NAME:
            calendar = cal
            break

    if not calendar:
        print(f"⚠️ Calendar '{CALENDAR_NAME}' not found.")
        return

    # Clear all events from the calendar before adding new ones
    print("🧹 Clearing existing events...")
    for event in calendar.events():
        event.delete()
    print("✅ All events cleared.")

    # Create events from the CSV
    create_events_from_csv(calendar)

if __name__ == "__main__":
    main()
