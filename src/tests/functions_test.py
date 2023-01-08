"""
File with tests for functions module.
"""
import os
import json
import pytest
import functions


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

    async def get_id(self, role):
        return self.storage.get(role)


class RedisMock:
    """
    Mock for Redis class.
    """
    storage = {
        "users": {
            "limiroshnichenko": 450,
            "ivpostnikov": 28
        }
    }
    async def exists(self, key: str) -> int:
        if key in self.storage:
            return 1
        return 0

    async def hget(self, key: str, slug: str) -> int:
        return self.storage.get(key).get(slug)

    async def hset(self, key, mapping):
        pass

    async def delete(self, role):
        pass


DATA = json.loads("""
[
    {
        "due_date": "2022-03-02",
        "subject": "Ошибки при отправке часов в кабинет"
    },
    {
        "due_date": "2022-10-01",
        "subject": "Express.js"
    },
    {
        "due_date": null,
        "subject": "Реализация locations"
    }
]
""")
EXPECTED = """
BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Ошибки при отправке часов в кабинет
DTSTART;TZID=Europe/Moscow:20220302T230000
END:VEVENT
BEGIN:VEVENT
SUMMARY:Express.js
DTSTART;TZID=Europe/Moscow:20221001T230000
END:VEVENT
END:VCALENDAR
""".strip()


def test_checkenv_giveexistingname_pass():
    os.environ["EXISTING_NAME"] = "10"
    functions.check_env("EXISTING_NAME")


def test_checkenv_givenotexistingname_raiseserror():
    with pytest.raises(KeyError):
        functions.check_env("NOT_EXISTING_NAME")


def test_converttaskstocalendar_givedict_returncalendar():
    func_result = functions.convert_tasks_to_calendar("Europe/Moscow", DATA)
    assert func_result.decode().strip().replace("\r", "") == EXPECTED


@pytest.mark.asyncio
async def test_getfromcache_givecachedroleexistedname_returnid():
    result = await functions.get_from_cache(
        RedisMock(),
        TaigaClientMock(),
        "users",
        "limiroshnichenko"
    )
    assert result == 450


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedroleexistedname_returnid():
    result = await functions.get_from_cache(
        RedisMock(),
        TaigaClientMock(),
        "projects",
        "370"
    )
    assert result == 18


@pytest.mark.asyncio
async def test_getgromcache_givenotcachedobjectbutesisted_refreshcacheretid():
    result = await functions.get_from_cache(
        RedisMock(),
        TaigaClientMock(),
        "users",
        "adpiskunov"
    )
    assert result == 29


@pytest.mark.asyncio
async def test_getfromcache_givenotcachedrolenotexistedname_returnnone():
    result = await functions.get_from_cache(
        RedisMock(),
        TaigaClientMock(),
        "projects",
        "19102"
    )
    assert result is None


@pytest.mark.asyncio
async def test_getgromcache_givenotcachedobjectnotesisted_returnnone():
    result = await functions.get_from_cache(
        RedisMock(),
        TaigaClientMock(),
        "users",
        "abobus"
    )
    assert result is None
