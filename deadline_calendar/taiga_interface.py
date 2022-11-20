import aioredis
import httpx


class TaigaInterface:
    ROLES = {
        "projects": {
            "taiga_sort": "project",
            "string_id": "slug"
        },
        "users": {
            "taiga_sort": "assigned_to",
            "string_id": "username"
        }
    }

    def __init__(self, base_url: str, token: str, redis_addres: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "x-disable-pagination": "True"
            }
        )
        self.redis = aioredis.from_url(redis_addres, decode_responses=True)

    async def __get_id(self, role: str, slug: str) -> int:
        if await self.redis.exists(role):
            return await self.redis.hget(role, slug)
        res = await self.client.get(f"/api/v1/{role}")
        objects = {
            elem[self.ROLES[role]["string_id"]]: elem["id"]
            for elem in res.json()
        }
        await self.redis.hset(role, mapping=objects)
        await self.redis.expire(role, 86400)
        return objects.get(slug)

    async def get_project_id(self, slug: str) -> int:
        return await self.__get_id("projects", slug)

    async def get_user_id(self, slug: str) -> int:
        return await self.__get_id("users", slug)

    async def __get_tasks(self, role: str, slug: str) -> list[dict]:
        object_id = self.__get_id(role, slug)
        if object_id is None:
            return None
        tasks = await self.client.get(
            "/api/v1/tasks",
            params={self.ROLES[role]["taiga_sort"]: id}
        )
        return tasks.json()

    async def get_project_tasks(self, slug: str) -> list[dict]:
        return await self.__get_tasks("projects", slug)

    async def get_user_tasks(self, slug: str) -> list[dict]:
        return await self.__get_tasks("users", slug)

    async def close(self):
        await self.client.aclose()
        await self.redis.close()
