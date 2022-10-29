from datetime import datetime
import json
import re
import os
from fastapi import APIRouter, Response, status
from icalendar import Calendar, Event
from dotenv import load_dotenv
import aioredis
import httpx
import pytz


load_dotenv()
try:
    TAIGA_URL = os.environ["TAIGA_URL"]
    TAIGA_TOKEN = os.environ["TAIGA_TOKEN"]
except KeyError:
    print(
        "--- WARNING ---\n\n"
        "TAIGA_URL and TAIGA_TOKEN must be specified.\n\n"
        "--- WARNING ---\n\n"
    )
    raise Exception()
TZ = os.getenv("TZ", "Europe/Moscow")
HEADER = {
    "Authorization": f"Bearer {TAIGA_TOKEN}",
    "x-disable-pagination": "True"
}


router = APIRouter()


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


@router.get("/calendar/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]
    if await red.exists("users"):
        user_id = json.loads(await red.get("users")).get(user_slug)
    else:
        res = await client.get("/api/v1/users", headers=HEADER)
        hash = {elem["username"]: elem["id"] for elem in res.json()}
        await red.set(
            "users",
            json.dumps(hash),
            ex=86400
        )
        user_id = hash.get(user_slug)

    if user_id is None:
        return Response(
            content=f"No student with name \"{user_slug}\"",
            media_type="text/plain",
            status_code=status.HTTP_404_NOT_FOUND
        )

    tasks = await client.get(
        f"/api/v1/tasks?assigned_to={user_id}",
        headers=HEADER
    )

    return Response(
        content=read_tasks(tasks.json()),
        media_type="text/calendar"
    )


@router.get("/calendar/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()
    if await red.exists("projects"):
        project_id = json.loads(await red.get("projects")).get(slug)
    else:
        res = await client.get("/api/v1/projects", headers=HEADER)
        hash = {elem["slug"]: elem["id"] for elem in res.json()}
        await red.set(
            "projects",
            json.dumps(hash),
            ex=86400
        )
        project_id = hash.get(slug)
    
    if project_id is None:
        return Response(
            content=f"No project with slug \"{slug}\"",
            media_type="text/plain",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    tasks = await client.get(
        f"/api/v1/tasks?project={project_id}",
        headers=HEADER
    )

    return Response(
        content=read_tasks(tasks.json()),
        media_type="text/calendar"
    )
