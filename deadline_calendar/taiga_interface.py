import aioredis
import httpx


class TaigaInterface:
    ROLES = {  # TODO Projects and users
        "project": {
            "string_id": "slug"
        },
        "user": {
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
    
    async def get_id(self, role: str, slug: str) -> int:
        if await self.redis.exists(role):
            return await self.redis.hget(role, slug)
        res = self.client.get(f"/api/v1/{role}")
        objects = {
            elem[self.ROLES[role]["string_id"]]: elem["id"]
            for elem in res.json()
        }
        await self.redis.hset(role, mapping=objects)
        await self.redis.expire(role, 86400)
        return objects.get(slug)

    async def get_project_id(self, slug: str) -> int:
        return await self.get_id("projects", slug)

    async def get_user_id(self, slug: str) -> int:
        return await self.get_id("users", slug)
    
    async def get_tasks(self, role: str, slug: str) -> list[dict]:
        id = self.get_id(role, slug)
        tasks = self.client.get("/api/v1/tasks", params={self.ROLES[role]})

    async def get_projects_tasks(self, slug: str) -> list[dict]:
        project_id = self.get_project_id(slug)
        res = await self.client.get("/api/v1/tasks", params={"project": project_id})

    async def get_users_tasks(self, slug: str) -> list[dict]:
        pass

    async def close(self):
        await self.client.aclose()
        await self.redis.close()
