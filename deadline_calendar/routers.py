import os
from responses import NO_STUDENT, NO_PROJECT, serialize_calendar
from taiga_interface import TaigaInterface
from functions import check_env, get_from_cache
from dotenv import load_dotenv
from fastapi import APIRouter
import aioredis


load_dotenv()
check_env(
    "TAIGA_URL",
    "TAIGA_TOKEN",
    "REDIS_CONNSTRING"
)
DEFAULT_TZ = "Europe/Moscow"
router = APIRouter()


@router.on_event("startup")
async def start():
    global taiga_client
    global redis
    taiga_client = TaigaInterface(
        os.environ["TAIGA_URL"],
        os.environ["TAIGA_TOKEN"],
        os.environ["REDIS_CONNSTRING"]
    )
    redis = aioredis.from_url(
        os.environ["REDIS_CONNSTRING"],
        decode_responses=True
    )


@router.on_event("shutdown")
async def stop():
    global taiga_client
    global redis
    await taiga_client.close()
    await redis.close()


@router.get("/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]

    user_id = await get_from_cache(redis, taiga_client, "users", user_slug)
    if user_id is None:
        return NO_STUDENT

    tasks = await taiga_client.get_user_tasks(user_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()

    project_id = await get_from_cache(redis, taiga_client, "projects", slug)
    if project_id is None:
        return NO_PROJECT

    tasks = await taiga_client.get_project_tasks(project_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)
