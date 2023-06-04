from fastapi import FastAPI

from src.controller.health import health_router
from src.controller.media import media_router
from src.controller.user import usr_router

app = FastAPI()

app.include_router(health_router, prefix="/v1")
app.include_router(media_router, prefix="/v1")
app.include_router(usr_router, prefix="/v1")
