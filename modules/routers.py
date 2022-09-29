from datetime import datetime
import re
from settings import HEADER, TZ, ROOT_PATH
from fastapi import APIRouter, Response
from icalendar import Calendar, Event
import requests
import pytz


router = APIRouter(prefix=ROOT_PATH.rstrip("/"))


@router.get("/calendar/{email}")
def make_calendar(email: str):
    ical = Calendar()
    user_slug = email.split("@")[0]
    tasks = requests.get(
        "https://track.miem.hse.ru/api/v1/tasks",
        headers=HEADER
    ).json()

    # users = requests.get(
    #     "https://track.miem.hse.ru/api/v1/users",
    #     headers=HEADER
    # ).json()
    # for user in users:
    #     if user["username"] == user_slug:
    #         user_id = user["id"]

    for task in tasks:
        if task["assigned_to"] is None:
            continue
        if task["assigned_to_extra_info"]["username"] == user_slug \
                                    and task["due_date"] is not None:
            due_date = re.match(r"(\d\d\d\d)-(\d\d)-(\d\d)", task["due_date"])
            event = Event()
            event.add("dtstart", datetime(
                int(due_date[1]),
                int(due_date[2]),
                int(due_date[3]),
                23, 0, tzinfo=pytz.timezone(TZ)
            ))
            event.add("summary", task["subject"])
            ical.add_component(event)
    
    return Response(content=ical.to_ical(), media_type="text/calendar")