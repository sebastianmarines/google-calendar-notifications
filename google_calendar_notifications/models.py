from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import List, Optional

from gcsa.event import Event
from schedule import Job


@dataclass
class ScheduledEvent:
    title: str
    description: str
    time: datetime.date
    location: Optional[str]
    id: str
    alerts: List[datetime.date]
    jobs: List[Job]

    @classmethod
    def from_gcsa_event(cls, event: Event) -> ScheduledEvent:
        return ScheduledEvent(event.summary, event.description, event.start,
                              event.location, event.event_id, event.reminders,
                              [])
