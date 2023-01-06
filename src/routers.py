"""
Module that contains endpoint of service.
"""
import os
import aioredis
from fastapi import APIRouter
from dotenv import load_dotenv
from taiga_interface import TaigaInterface
from functions import check_env, get_from_cache
from responses import NO_STUDENT, NO_PROJECT, serialize_calendar


load_dotenv()
check_env(
    "TAIGA_URL",
    "TAIGA_TOKEN",
    "REDIS_CONNSTRING"
)
DEFAULT_TZ = "Europe/Moscow"
TAIGA_CLIENT = None
REDIS = None
router = APIRouter()


@router.on_event("startup")
async def start():
    global TAIGA_CLIENT  # pylint: disable=global-statement
    global REDIS  # pylint: disable=global-statement
    TAIGA_CLIENT = TaigaInterface(
        os.environ["TAIGA_URL"],
        os.environ["TAIGA_TOKEN"]
    )
    REDIS = aioredis.from_url(
        os.environ["REDIS_CONNSTRING"],
        decode_responses=True
    )


@router.on_event("shutdown")
async def stop():
    await TAIGA_CLIENT.close()
    await REDIS.close()


@router.get("/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]

    user_id = await get_from_cache(REDIS, TAIGA_CLIENT, "users", user_slug)
    if user_id is None:
        return NO_STUDENT

    tasks = await TAIGA_CLIENT.get_user_tasks(user_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()

    project_id = await get_from_cache(REDIS, TAIGA_CLIENT, "projects", slug)
    if project_id is None:
        return NO_PROJECT

    tasks = await TAIGA_CLIENT.get_project_tasks(project_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)
