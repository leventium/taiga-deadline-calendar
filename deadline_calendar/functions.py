import os
import re
from datetime import datetime
from icalendar import Calendar, Event
import pytz


def check_env(*args: str):
    for name in args:
        if os.getenv(name) is None:
            raise KeyError(
                f"No environment variable with name {name}. "
                f"{args} must be specified."
            )


def convert_tasks_to_calendar(tz: str, tasks: list[dict]) -> bytes:
    ical = Calendar()
    for task in tasks:
        if task["due_date"] is not None:
            event = Event()
            due_date = re.match(r"(\d\d\d\d)-(\d\d)-(\d\d)", task["due_date"])
            event.add("dtstart", datetime(
                int(due_date[1]),
                int(due_date[2]),
                int(due_date[3]),
                23, 0, tzinfo=pytz.timezone(tz)
            ))
            event.add("summary", task["subject"])
            ical.add_component(event)
    return ical.to_ical()
