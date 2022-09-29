from fastapi import FastAPI
from modules.routers import router


app = FastAPI()
app.include_router(router)