import aioredis
import httpx


class TaigaInterface:
    def __init__(self, base_url: str, token: str, redis_addres: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "x-disable-pagination": "True"
            }
        )
        self.redis = aioredis.from_url(redis_addres, decode_responses=True)
    
    async def get_project_id(self, slug: str) -> int:
        if await self.redis.exists("projects"):
            projects = await self.redis.hgetall("projects")
            return projects.get(slug)
        res = self.client.get("/api/v1/projects")
        projects = {elem["slug"]: elem["id"] for elem in res.json()}
        await self.redis.hset("projects", mapping=projects)
        await self.redis.expire("projects", 86400)
        return projects.get(slug)

    async def close(self):
        await self.client.aclose()
        await self.redis.close()