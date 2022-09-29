from fastapi import FastAPI
from modules.routers import router
import uvicorn

app = FastAPI()
app.include_router(router)
