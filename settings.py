ROOT_PATH = ""    # /
TAIGA_URL = ""    # https://sitename.example
TAIGA_TOKEN = ""  # JWT

TZ = "Europe/Moscow"

HEADER = {
    "Authorization": "Bearer " + TAIGA_TOKEN,
    "x-disable-pagination": "True"
}