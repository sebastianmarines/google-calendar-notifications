import time
from pathlib import Path
from typing import List
from google.oauth2.credentials import Credentials

import schedule

from google_calendar_notifications.helpers import (authenticate_user,
                                                   get_calendars, get_events,
                                                   schedule_job_for_event,
                                                   show_notification)
from google_calendar_notifications.models import ScheduledEvent
from google_calendar_notifications.settings import APP_DIRECTORY


def update_event_list(creds: Credentials, calendar_ids: List[str],
                      scheduled_events: dict[str, ScheduledEvent]):
    events = get_events(creds, calendar_ids)

    for event in events:
        if event.event_id in scheduled_events:
            if (existing_event :=
                    scheduled_events[event.event_id]).time != event.start:
                existing_event.time = event.start
                for job in existing_event.jobs:
                    schedule.cancel_job(job)
                schedule_job_for_event(existing_event)
                scheduled_events[event.event_id] = existing_event

        else:
            new_event = ScheduledEvent.from_gcsa_event(event)
            schedule_job_for_event(new_event)
            scheduled_events[new_event.id] = new_event


def main():
    if not APP_DIRECTORY.exists():
        Path.mkdir(APP_DIRECTORY)
    creds = authenticate_user()
    calendar_ids = get_calendars()

    scheduled_events: dict[str, ScheduledEvent] = dict()

    update_event_list(creds, calendar_ids, scheduled_events)

    schedule.every(10).minutes.do(update_event_list, creds, calendar_ids,
                                  scheduled_events)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
