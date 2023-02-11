"""
Module with Cache class that provides communication with Redis.
"""
import aioredis


class Cache:
    def __init__(self, connstring: str) -> None:
        self.redis = aioredis.from_url(connstring)

    async def close(self):
        await self.redis.close()

    async def __set(self, role: str, data: dict[str, str]) -> None:
        await self.redis.delete(role)
        await self.redis.hset(role, mapping=data)

    async def __get(self, role: str, slug: str) -> None:
        return await self.redis.hget(role, slug)

    async def get_user(self, slug: str) -> str:
        return await self.__get("users", slug)

    async def get_project(self, slug: str) -> str:
        return await self.__get("projects", slug)

    async def set_users(self, users: dict[str, str]) -> None:
        await self.__set("users", users)

    async def set_projects(self, projects: dict[str, str]) -> None:
        await self.__set("projects", projects)
