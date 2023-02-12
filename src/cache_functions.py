"""
Module with fuctions that use cache.
"""


async def get_user_from_cache_or_refresh(
            cache,
            taiga_client,
            slug: str) -> int:
    user_id = await cache.get_user(slug)
    if user_id is None:
        users_hash = await taiga_client.get_users()
        await cache.set_users(users_hash)
        return users_hash.get(slug)
    return int(user_id)


async def get_project_from_cache_or_refresh(
            cache,
            taiga_client,
            slug: str) -> int:
    project_id = await cache.get_project(slug)
    if project_id is None:
        projects_hash = await taiga_client.get_projects()
        await cache.set_projects(projects_hash)
        return projects_hash.get(slug)
    return int(project_id)
