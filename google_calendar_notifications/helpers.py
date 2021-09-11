import datetime
from google_calendar_notifications.models import ScheduledEvent
import json
from typing import List, Optional, Type

import notify2
import schedule
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from google_calendar_notifications import app_name
from google_calendar_notifications.settings import (APP_DIRECTORY, CREDENTIALS,
                                                    SCOPES)


def authenticate_user() -> Credentials:
    """Authenticate a user with their Google account

    Returns:
        Credentials: Google OAuth2 credentials
    """
    creds: Optional[Credentials] = None

    creds_file = APP_DIRECTORY / "token.json"

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
    return creds


def get_calendars() -> List[str]:
    """Get a list of the calendars that the user wants to retrieve

    Returns:
        List[str]: List of calendars
    """
    calendars_file = APP_DIRECTORY / "calendars.json"

    if calendars_file.exists():
        with open(calendars_file) as file:
            return json.load(file)
    else:
        with open(calendars_file, "w") as file:
            default_calendars = ["primary"]
            json.dump(default_calendars, file, indent=4)
            return default_calendars


def get_events(creds: Credentials, calendar_ids: List[str]) -> List[Event]:
    """Get all the events from the specified calendars

    Args:
        creds (Credentials): Google OAuth2 credentials
        calendar_ids (List[str]): A list of the calendars to check

    Returns:
        List[Event]: A list of events
    """
    today = datetime.date.today()
    time_min = datetime.datetime.combine(today, datetime.datetime.min.time())
    time_max = datetime.datetime.combine(today, datetime.datetime.max.time())

    calendars: List[GoogleCalendar] = [
        GoogleCalendar(credentials=creds, calendar=cal_id)
        for cal_id in calendar_ids
    ]

    return [
        event for calendar in calendars
        for event in calendar.get_events(time_min=time_min, time_max=time_max)
        if event if event.start > datetime.datetime.now(event.start.tzinfo)
    ]


def show_notification(summary: str, message: Optional[str],
                      time: str) -> Type[schedule.CancelJob]:
    """Show a notification in the system

    Args:
        summary (str): The notification title
        message (Optional[str]): The notification body
        time (str): Event's start time

    Returns:
        Type[schedule.CancelJob]: Scheduled job
    """
    message = message if message else ""
    notify2.init(app_name)
    notification = notify2.Notification(summary=summary,
                                        message=time + "\n" + message,
                                        icon="calendar")
    notification.timeout = 15000
    notification.show()
    return schedule.CancelJob


def schedule_job_for_event(event: ScheduledEvent):
    event_time = event.time.strftime("%H:%M")
    event_job = schedule.every().day.at(event_time).do(show_notification,
                                                       event.title,
                                                       event.location,
                                                       event_time)

    event.jobs.append(event_job)
