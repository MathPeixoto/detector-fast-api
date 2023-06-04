import datetime

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/")
async def health():
    return {"datetime": datetime.datetime.now()}
