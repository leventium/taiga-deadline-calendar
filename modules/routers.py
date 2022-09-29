from fastapi import APIRouter
from icalendar import Calendar, Event
from .. import myset  # Change in prod

router = APIRouter()


@router.get("/calendar/{email}")
def make_calendar(email: str):
    pass