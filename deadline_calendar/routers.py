from responses import NO_STUDENT, NO_PROJECT, serialize_calendar
from taiga_interface import TaigaInterface
from functions import check_env
from dotenv import load_dotenv
from fastapi import APIRouter


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
    taiga_client = TaigaInterface(
        os.environ("TAIGA_URL"),
        os.environ("TAIGA_TOKEN"),
        os.environ("REDIS_CONNSTRING")
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

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()

    tasks = taiga_client.get_project_tasks(slug)
    if tasks is None:
        return NO_PROJECT

    return serialize_calendar(os.getenv("TIME_ZONE", DEFAULT_TZ), tasks)
