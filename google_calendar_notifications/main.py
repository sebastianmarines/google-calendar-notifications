import datetime
from pathlib import Path
import time
from typing import List, Optional, Type
from dateutil import tz

import notify2
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import schedule

from google_calendar_notifications import app_name
from google_calendar_notifications.settings import CREDENTIALS, SCOPES


def show_notification(summary: str, message: Optional[str]):
    message = message if message else ""
    notify2.init(app_name)
    notification = notify2.Notification(summary=summary,
                                        message=message,
                                        icon="calendar")
    notification.timeout = 15000
    notification.show()
    return schedule.CancelJob


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
    today = datetime.date.today()
    time_min = datetime.datetime.combine(today, datetime.datetime.min.time())
    time_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    calendars: List[GoogleCalendar] = [
        GoogleCalendar(credentials=creds, calendar=cal_id)
        for cal_id in calendar_ids
    ]

    events: List[Event] = [
        event for calendar in calendars
        for event in calendar.get_events(time_min=time_min, time_max=time_max)
        if event if event.start > datetime.datetime.now(event.start.tzinfo)
    ]

    scheduled_events: set[str] = set()

    for event in events:
        if event.event_id in scheduled_events:
            continue
        schedule.every().day.at(event.start.strftime("%H:%M")).do(
            show_notification, event.summary, event.description)
        scheduled_events.add(event.event_id)

    while True:
        schedule.run_pending()
        time.sleep(1)
