from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)

# Function to authenticate Google API
def authenticate():
    creds = None
    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, prompt user to sign in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save new credentials to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Function to add event to calendar
def add_event(summary, start_time, end_time, calendar_id='primary'):
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()

# API route to add event
@app.route('/add_event', methods=['POST'])
def api_add_event():
    data = request.json
    summary = data.get('summary')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    category = data.get('category', 'primary')
    add_event(summary, start_time, end_time, category)
    return jsonify({"message": f"Event '{summary}' added successfully!"})

# Do not use app.run() on Vercel. It handles the serverless functions.
if __name__ == "__main__":
    app.run(debug=True)
