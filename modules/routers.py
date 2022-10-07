from datetime import datetime
import json
import re
from settings import HEADER, TZ, ROOT_PATH, TAIGA_URL
from fastapi import APIRouter, Response
from icalendar import Calendar, Event
import aioredis
import httpx
import pytz


router = APIRouter(prefix=ROOT_PATH.rstrip("/"))


@router.on_event("startup")
async def start():
    global client
    global red
    client = httpx.AsyncClient(base_url=TAIGA_URL.rstrip("/"))
    red = aioredis.from_url("redis://redis")


@router.on_event("shutdown")
async def stop():
    global client
    global red
    await client.aclose()
    await red.close()


@router.get("/calendar/{email}")
async def make_calendar(email: str):
    ical = Calendar()
    user_slug = email.split("@")[0]
    if await red.exists("users"):
        user_id = json.loads(await red.get("users"))[user_slug]
    else:
        res = await client.get("/api/v1/users", headers=HEADER)
        hash = {elem["username"]: elem["id"] for elem in res.json()}
        await red.set(
            "users",
            json.dumps(hash),
            ex=86400
        )
        user_id = hash[user_slug]
    tasks = await client.get(
        f"/api/v1/tasks?assigned_to={user_id}",
        headers=HEADER
    )

    for task in tasks.json():
        if task["due_date"] is not None:
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