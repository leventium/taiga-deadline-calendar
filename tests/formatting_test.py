"""
File with tests for formatting module.
"""
import sys
sys.path.append("..")
import json
from src import formatting


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


def test_converttaskstocalendar_givedict_returncalendar():
    func_result = formatting.convert_tasks_to_calendar("Europe/Moscow", DATA)
    assert func_result.decode().strip().replace("\r", "") == EXPECTED
