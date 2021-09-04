from pathlib import Path
from typing import List, Optional

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from google_calendar_notifications.settings import CREDENTIALS, SCOPES

if __name__ == "__main__":
    home = Path.home()
    app_directory = home / ".google-calendar-notifications"
    if not app_directory.exists():
        Path.mkdir(app_directory)

    creds: Optional[Credentials] = None

    creds_file = app_directory / "token.json"

    if creds_file.exists():
        creds = Credentials.from_authorized_user_file(creds_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(creds_file, 'w') as token:
            token.write(creds.to_json())
    calendar_ids = [
        'primary', 'ii0ct0rqg5vrnpq7v5dtrojnn4@group.calendar.google.com',
        'ejab4nspdr9q0mku2gjp860f20@group.calendar.google.com'
    ]

    calendars: List[GoogleCalendar] = [
        GoogleCalendar(credentials=creds, calendar=cal_id)
        for cal_id in calendar_ids
    ]

    events: List[Optional[Event]] = [
        event for calendar in calendars for event in calendar.get_events()
    ]

    for event in events:
        if event:
            print("Reminders: ", event.reminders)
            print("Start date: ", event.start)
            print("Description: ", event.description)
            print("Summary: ", event.summary)
            print("-----")
