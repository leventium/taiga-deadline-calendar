"""
Main file of this project.
"""
import os
import uvicorn
from fastapi import FastAPI
from routers import router


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
