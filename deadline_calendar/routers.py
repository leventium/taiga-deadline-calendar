from responses import NO_STUDENT, NO_PROJECT, serialize_calendar
from taiga_interface import TaigaInterface
from functions import get_env
from fastapi import APIRouter


env = get_env()
router = APIRouter()


@router.on_event("startup")
async def start():
    global taiga_client
    taiga_client = TaigaInterface(
        env["TAIGA_URL"],
        env["TAIGA_TOKEN"],
        env["REDIS_CONNSTRING"]
    )


@router.on_event("shutdown")
async def stop():
    global taiga_client
    await taiga_client.close()


@router.get("/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]

    tasks = taiga_client.get_user_tasks(user_slug)
    if tasks is None:
        return NO_STUDENT

    return serialize_calendar(env["TZ"], tasks)


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()

    tasks = taiga_client.get_project_tasks(slug)
    if tasks is None:
        return NO_PROJECT

    return serialize_calendar(env["TZ"], tasks)
