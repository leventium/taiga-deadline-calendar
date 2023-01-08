"""
Module that contains clear functions with
environment checking, serialization, caching.
"""
import os
import re
from datetime import datetime
import pytz
from icalendar import Calendar, Event


DATE_PATTERN = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)")


def check_env(*args: str):
    for name in args:
        if os.getenv(name) is None:
            raise KeyError(
                f"No environment variable with name {name}. "
                f"{args} must be specified."
            )


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


async def get_from_cache(redis, taiga_client, role: str, slug: str):
    if await redis.exists(role):
        obj_id = await redis.hget(role, slug)
        if obj_id is None:
            obj_hash = await taiga_client.get_id(role)
            await redis.delete(role)
            await redis.hset(role, mapping=obj_hash)
            return obj_hash.get(slug)
        return int(obj_id)
    obj_hash = await taiga_client.get_id(role)
    await redis.hset(role, mapping=obj_hash)
    return obj_hash.get(slug)
