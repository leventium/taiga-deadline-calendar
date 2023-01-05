from functions import convert_tasks_to_calendar
from fastapi import Response, status
from fastapi.responses import JSONResponse


NO_STUDENT = JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content={
        "error": {
            "message": "No student with this slug or email."
        }
    },
    media_type="application/json"
)

NO_PROJECT = JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content={
        "error": {
            "message": "No project with this slug."
        }
    },
    media_type="application/json"
)


def serialize_calendar(time_zone: str, tasks: list[dict]) -> Response:
    return Response(
        content=convert_tasks_to_calendar(time_zone, tasks),
        media_type="text/calendar"
    )
