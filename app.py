from dotenv import load_dotenv
from fastapi import FastAPI
from controller.user import router, idp

load_dotenv()
app = FastAPI()
idp.add_swagger_config(app)

app.include_router(router, prefix="/user")
