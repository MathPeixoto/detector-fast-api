import os

import boto3
from dotenv import load_dotenv

load_dotenv()

settings = {
    "COGNITO_POOL_URL": os.getenv("COGNITO_POOL_URL"),
    "APP_CLIENT_ID": os.getenv("APP_CLIENT_ID"),
    "AWS_REGION": os.getenv("AWS_REGION"),
    "AWS_SECRET_KEY": os.getenv("AWS_SECRET_KEY"),
}

client_id = settings["APP_CLIENT_ID"]
client_secret = settings["AWS_SECRET_KEY"]
region = settings["AWS_REGION"]

client = boto3.client("cognito-idp", region_name=region)