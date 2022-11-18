import json
from functions import get_env, read_tasks
from taiga_interface import TaigaInterface
from fastapi import APIRouter, Response, status
import aioredis
import httpx


env = get_env()         # TODO !!!
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

# TODO Исправить env и включить интерфейс, вывести константы в отдельные файлы

@router.get("/person/{email}")
async def make_calendar(email: str):
    user_slug = email.lower().split("@")[0]
    if await red.exists("users"):
        user_id = json.loads(await red.get("users")).get(user_slug)
    else:
        res = await taiga_client.get("/api/v1/users", headers=HEADER)
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

    tasks = await taiga_client.get(
        f"/api/v1/tasks?assigned_to={user_id}",
        headers=HEADER
    )

    return Response(
        content=read_tasks(tasks.json()),
        media_type="text/calendar"
    )


@router.get("/project/{slug}")
async def make_project_calendar(slug: str):
    slug = slug.lower()
    if await red.exists("projects"):
        project_id = json.loads(await red.get("projects")).get(slug)
    else:
        res = await taiga_client.get("/api/v1/projects", headers=HEADER)
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
    
    tasks = await taiga_client.get(
        f"/api/v1/tasks?project={project_id}",
        headers=HEADER
    )

    return Response(
        content=read_tasks(tasks.json()),
        media_type="text/calendar"
    )
