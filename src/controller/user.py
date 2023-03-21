from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi_keycloak import OIDCUser

from src.conf.keycloak import config_keycloak

router = APIRouter()
idp = config_keycloak()


@router.get("/")  # Unprotected
def root():
    return 'Hello World'


@router.get("/user")  # Requires to be logged in
def current_users(user: OIDCUser = Depends(idp.get_current_user())) -> OIDCUser:
    return user


@router.get("/admin")  # Requires the admin role
def company_admin(user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"]))):
    return f'Hi admin {user}'


@router.get("/login")
def login_redirect():
    return RedirectResponse(idp.login_uri)


@router.get("/callback")
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token
