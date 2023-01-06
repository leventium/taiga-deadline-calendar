"""
Module that provides high-level interface of taiga api.
"""
# import aioredis
import httpx


class TaigaInterface:
    """
    Class of interface, represents a instance of taiga.
    """
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

    def __init__(self, base_url: str, token: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "x-disable-pagination": "True"
            }
        )
        # self.redis = aioredis.from_url(redis_addres, decode_responses=True)

    async def get_id(self, role: str) -> dict:
        """
        Общая функция для получание списка объектов тайги в формате {name: id},
        позволяет в дальнейшем получить id объекта имея его имя.
        (Удобно кэшировать :) )
        role -- тип объекта для которого нужно получить список.
        """
        # if await self.redis.exists(role):
        #     return await self.redis.hget(role, slug)
        res = await self.client.get(f"/api/v1/{role}")
        objects = {
            elem[self.ROLES[role]["string_id"]]: elem["id"]
            for elem in res.json()
        }
        # await self.redis.hset(role, mapping=objects)
        # await self.redis.expire(role, 86400)
        return objects

    async def get_project_id(self) -> dict:
        return await self.get_id("projects")

    async def get_user_id(self) -> dict:
        return await self.get_id("users")

    async def __get_tasks(self, role: str, object_id: int) -> list[dict]:
        # object_id = self.__get_id(role, slug)
        # if object_id is None:
        #     return None
        tasks = await self.client.get(
            "/api/v1/tasks",
            params={self.ROLES[role]["taiga_sort"]: object_id}
        )
        return tasks.json()

    async def get_project_tasks(self, project_id: int) -> list[dict]:
        return await self.__get_tasks("projects", project_id)

    async def get_user_tasks(self, user_id: int) -> list[dict]:
        return await self.__get_tasks("users", user_id)

    async def close(self):
        await self.client.aclose()
        # await self.redis.close()
