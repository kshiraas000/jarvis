from google.auth.transport.requests import Request
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import dateparser

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
    creds = None

    # Check for token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, prompt the user to sign in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save new credentials to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Return the service object instead of just credentials
    return build('calendar', 'v3', credentials=creds)

def add_event(summary, start_time, end_time):
    service = authenticate()  # Get the service directly
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'}
    }
    service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event '{summary}' added!")

def parse_event(command):
    # Example: "Lunch with Sarah tomorrow at noon"
    parts = command.split(" at ")
    if len(parts) != 2:
        print("Invalid format. Please say the event in the format 'Event at time'.")
        return None, None, None

    summary = parts[0].strip().capitalize()
    start_time = dateparser.parse(parts[1].strip())
    if not start_time:
        print("Could not parse the time. Please try again.")
        return None, None, None

    end_time = start_time + timedelta(hours=1)  # Default 1-hour duration
    return summary, start_time.isoformat(), end_time.isoformat()