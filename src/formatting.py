"""
Module that contains clear functions with
environment checking, serialization, caching.
"""
import re
from datetime import datetime
import pytz
from icalendar import Calendar, Event


DATE_PATTERN = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)")


def convert_tasks_to_calendar(time_zone: str, tasks: list[dict]) -> bytes:
    ical = Calendar()
    for task in tasks:
        if task["due_date"] is not None:
            event = Event()
            due_date = DATE_PATTERN.match(task["due_date"])
            event.add("dtstart", datetime(
                int(due_date[1]),
                int(due_date[2]),
                int(due_date[3]),
                23, 0, tzinfo=pytz.timezone(time_zone)
            ))
            event.add("summary", task["subject"])
            ical.add_component(event)
    return ical.to_ical()
