from fastapi import FastAPI

from src.controller.user import router

app = FastAPI()

app.include_router(router, prefix="/v1")
