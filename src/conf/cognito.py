import base64
import hashlib
import hmac
import json
from typing import Dict, List, Optional

import boto3
import jose.constants
import jose.jwk
import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.conf.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



class CognitoAuth:
    def __init__(self):
        self.app_client_id = settings["APP_CLIENT_ID"]
        self.client_secret = settings["AWS_SECRET_KEY"]
        self.cognito_pool_url = settings["COGNITO_POOL_URL"]
        self.jwks_url = f"{self.cognito_pool_url}/.well-known/jwks.json"
        self.client = boto3.client("cognito-idp", region_name=settings["AWS_REGION"])

    @staticmethod
    def get_unverified_header(token: str) -> Dict[str, str]:
        try:
            return jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid JWT token")

    @staticmethod
    def find_key(kid: str, jwks: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        for jwk in jwks:
            if jwk["kid"] == kid:
                return jwk
        return {}

    @staticmethod
    def extract_roles(decoded_token: Dict[str, str]) -> List[str]:
        roles_claim = "cognito:groups"
        return decoded_token.get(roles_claim, [])

    def get_jwks(self) -> List[Dict[str, str]]:
        response = requests.get(self.jwks_url)
        return json.loads(response.text)["keys"]

    def decode_jwt(self, token: str) -> Dict[str, str]:
        headers = self.get_unverified_header(token)
        jwks = self.get_jwks()
        key = self.find_key(headers["kid"], jwks)
        if not key:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid JWT token")
        pem_key = jose.jwk.construct(key, jose.constants.Algorithms.RS256).to_pem()
        return jwt.decode(token, pem_key, algorithms=["RS256"], audience=self.app_client_id)

    def get_secret_hash(self, username: str) -> str:
        msg = username + self.app_client_id
        dig = hmac.new(self.client_secret.encode("utf-8"), msg=msg.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def get_tokens(self, username: str, password: str) -> Dict[str, str]:
        secret_hash = self.get_secret_hash(username)
        return self.client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash
            },
            ClientId=self.app_client_id
        )


cognito_auth = CognitoAuth()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, List[str]]:
    decoded_token = cognito_auth.decode_jwt(token)
    user = {"username": decoded_token["cognito:username"], "roles": cognito_auth.extract_roles(decoded_token)}
    return user


async def is_admin(current_user: Dict[str, List[str]] = Depends(get_current_user)) -> Dict[str, List[str]]:
    if "admin" not in current_user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
