"""
File with tests for cache_functions module.
"""
import sys
sys.path.append("..")
import pytest
from src import cache_functions


class TaigaClientMock:  # pylint: disable=too-few-public-methods
    """
    Mock for taiga_interface class.
    """
    storage = {
        "users": {
            "limiroshnichenko": 450,
            "ivpostnikov": 28,
            "adpiskunov": 29
        },
        "projects": {
            "239": 2979,
            "370": 18,

        }
    }

    async def get_users(self):
        return self.storage["users"]

    async def get_projects(self):
        return self.storage["projects"]


class CacheMock:
    """
    Mock for Redis class.
    """
    storage = {
        "users": {
            "limiroshnichenko": "450",
            "ivpostnikov": "28"
        },
        "projects": {}
    }

    async def get_user(self, slug: str) -> str:
        return self.storage["users"].get(slug)

    async def get_project(self, slug: str) -> str:
        return self.storage["projects"].get(slug)

    async def set_users(self, users):
        pass

    async def set_projects(self, projects):
        pass


@pytest.mark.asyncio
async def test_getfromcache_givecachedroleexistedname_returnid():
    result = await cache_functions.get_user_from_cache_or_refresh(
        CacheMock(),
        TaigaClientMock(),
        "limiroshnichenko"
    )
    assert result == 450


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedroleexistedname_returnid():
    result = await cache_functions.get_project_from_cache_or_refresh(
        CacheMock(),
        TaigaClientMock(),
        "370"
    )
    assert result == 18


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedobjectbutesisted_refreshcacheretid():
    result = await cache_functions.get_user_from_cache_or_refresh(
        CacheMock(),
        TaigaClientMock(),
        "adpiskunov"
    )
    assert result == 29


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedrolenotexistedname_returnnone():
    result = await cache_functions.get_project_from_cache_or_refresh(
        CacheMock(),
        TaigaClientMock(),
        "19102"
    )
    assert result is None


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedobjectnotesisted_returnnone():
    result = await cache_functions.get_user_from_cache_or_refresh(
        CacheMock(),
        TaigaClientMock(),
        "abobus"
    )
    assert result is None
