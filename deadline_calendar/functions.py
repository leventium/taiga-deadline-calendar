import os
import re
from datetime import datetime
from icalendar import Calendar, Event
from dotenv import load_dotenv
import pytz


def get_env() -> dict:
    load_dotenv()
    env = {}
    try:
        env["TAIGA_URL"] = os.environ["TAIGA_URL"]
        env["TAIGA_TOKEN"] = os.environ["TAIGA_TOKEN"]
    except KeyError:
        print(
            "--- WARNING ---\n\n"
            "TAIGA_URL and TAIGA_TOKEN must be specified.\n\n"
            "--- WARNING ---\n\n"
        )
        raise Exception()
    env["TZ"] = os.getenv("TZ", "Europe/Moscow")
    return env

def read_tasks(tasks: list) -> bytes:
    ical = Calendar()
    for task in tasks:
        if task["due_date"] is not None:
            event = Event()
            due_date = re.match(r"(\d\d\d\d)-(\d\d)-(\d\d)", task["due_date"])
            event.add("dtstart", datetime(
                int(due_date[1]),
                int(due_date[2]),
                int(due_date[3]),
                23, 0, tzinfo=pytz.timezone(TZ)
            ))
            event.add("summary", task["subject"])
            ical.add_component(event)
    return ical.to_ical()
