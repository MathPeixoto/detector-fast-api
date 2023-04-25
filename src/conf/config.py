import os

from dotenv import load_dotenv

load_dotenv()

settings = {
    "COGNITO_POOL_URL": os.getenv("COGNITO_POOL_URL"),
    "APP_CLIENT_ID": os.getenv("APP_CLIENT_ID"),
    "AWS_REGION": os.getenv("AWS_REGION"),
    "AWS_SECRET_KEY": os.getenv("AWS_SECRET_KEY"),
}
