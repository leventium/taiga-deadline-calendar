"""
Module that contains endpoint of service.
"""
import os
from fastapi import APIRouter
from dotenv import load_dotenv
from taiga_interface import TaigaInterface
from caching import Cache
from cache_functions import (
    get_user_from_cache_or_refresh,
    get_project_from_cache_or_refresh
)
from responses import NO_STUDENT, NO_PROJECT, serialize_calendar


load_dotenv()
DEFAULT_TZ = "Europe/Moscow"
TAIGA_CLIENT = None
CACHE = None
router = APIRouter()


@router.on_event("startup")
async def start():
    global TAIGA_CLIENT  # pylint: disable=global-statement
    global CACHE  # pylint: disable=global-statement
    TAIGA_CLIENT = TaigaInterface(
        os.environ["TAIGA_URL"],
        os.environ["TAIGA_TOKEN"]
    )
    CACHE = Cache(os.environ["REDIS_CONNSTRING"])


@router.on_event("shutdown")
async def stop():
    await TAIGA_CLIENT.close()
    await CACHE.close()


@router.get("/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]

    user_id = await get_user_from_cache_or_refresh(
        CACHE,
        TAIGA_CLIENT,
        user_slug
    )
    if user_id is None:
        return NO_STUDENT

    tasks = await TAIGA_CLIENT.get_user_tasks(user_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()

    project_id = await get_project_from_cache_or_refresh(
        CACHE,
        TAIGA_CLIENT,
        slug
    )
    if project_id is None:
        return NO_PROJECT

    tasks = await TAIGA_CLIENT.get_project_tasks(project_id)

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)
