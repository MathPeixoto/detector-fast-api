from fastapi import APIRouter
from fastapi import Depends

from src.conf.cognito import get_current_user, is_admin

router = APIRouter()


@router.get("/")  # Unprotected
def root():
    return 'Hello World'


@router.get("/user")  # Requires to be logged in
def current_users(current_user=Depends(get_current_user)):
    return {"message": "This is a protected route for any authenticated user", "user": current_user}


@router.get("/admin")  # Requires to be logged in
async def admin_route(current_user=Depends(is_admin)):
    return {"message": "This is a protected route for admins only", "user": current_user}
