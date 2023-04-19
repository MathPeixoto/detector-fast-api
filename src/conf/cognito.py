import json

import jose.constants
import jose.jwk
import jwt
import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import settings

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

COGNITO_POOL_URL = settings["COGNITO_POOL_URL"]
APP_CLIENT_ID = settings["APP_CLIENT_ID"]
JWKS_URL = f"{COGNITO_POOL_URL}/.well-known/jwks.json"


def get_jwks():
    response = requests.get(JWKS_URL)
    return json.loads(response.text)["keys"]


def decode_jwt(token: str):
    jwks = get_jwks()

    try:
        headers = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid JWT token")

    kid = headers["kid"]

    key = {}
    for jwk in jwks:
        if jwk["kid"] == kid:
            key = jwk
            break

    if not key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid JWT token")

        # Convert the JWK key to a PEM key
    pem_key = jose.jwk.construct(key, jose.constants.Algorithms.RS256).to_pem()

    try:
        decoded_token = jwt.decode(token, pem_key, algorithms=["RS256"], audience=APP_CLIENT_ID)
        return decoded_token
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid JWT token: {str(e)}")


def extract_roles(decoded_token: dict):
    roles_claim = "cognito:groups"  # Change this if you're using a different claim for roles
    if roles_claim in decoded_token:
        return decoded_token[roles_claim]
    return []


async def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_token = decode_jwt(token)
    user = {"username": decoded_token["cognito:username"], "roles": extract_roles(decoded_token)}
    return user


async def is_admin(current_user=Depends(get_current_user)):
    if "admin" not in current_user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
