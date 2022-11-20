FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./deadline_calendar .

CMD ["python", "main.py"]