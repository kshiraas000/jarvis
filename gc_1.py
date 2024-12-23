from urllib.request import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import speech_recognition as sr
import dateparser
from datetime import datetime, timedelta
import pyttsx3
#hi

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    creds = None
    # Authenticate or refresh token
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    return creds

def add_event(summary, start_time, end_time):
    service = build('calendar', 'v3', credentials=authenticate_google())
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'}
    }
    service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event '{summary}' added!")

def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return None

def parse_event(command):
    # Example: "Lunch with Sarah tomorrow at noon"
    parts = command.split(" at ")
    summary = parts[0].strip()
    start_time = dateparser.parse(parts[1].strip())
    end_time = start_time + timedelta(hours=1)  # Default 1-hour duration
    return summary, start_time.isoformat(), end_time.isoformat()

def main():
    command = get_speech_input()
    if command:
        summary, start_time, end_time = parse_event(command)
        add_event(summary, start_time, end_time)

if __name__ == "__main__":
    main()

# def speak(message):
#     engine = pyttsx3.init()
#     engine.say(message)
#     engine.runAndWait()

# # Example:
# speak("Your event has been added successfully!")