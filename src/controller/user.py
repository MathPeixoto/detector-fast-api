from fastapi import APIRouter
from fastapi import Depends

from src.conf.cognito import is_admin, cognito_auth
from src.model.user import User

usr_router = APIRouter()


@usr_router.post("/token/")  # Unprotected
async def token(user: User):
    return cognito_auth.get_tokens(user.username, user.password)


@usr_router.get("/admin/")  # Requires to be logged in and to be admin
async def admin_route(current_user=Depends(is_admin)):
    return {"message": "This is a protected route for admins only", "user": current_user}
