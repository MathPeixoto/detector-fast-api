from dotenv import load_dotenv
from fastapi import FastAPI

from lib.mangum.adapter import Mangum
from src.controller.user import router

load_dotenv()
app = FastAPI()

handler = Mangum(app)

app.include_router(router, prefix="/v1")
