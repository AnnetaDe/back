from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.db.database import start_database
from app.db.models.user import User
from app.helpers.tokens import create_token


login_router = APIRouter()
database = start_database()


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    acc_token: str
    refresh_token: str
    type: str = "bearer"


@login_router.post("/login", response_model=UserLoginResponse)
async def api_login_user(data: UserLoginRequest):
    """Login a user."""

    user = User.verify_user_email_password(
        email=data.email, password=data.password, db=database
    )

    if not user:
        return HTTPException(status_code=401, detail="Invalid email or password")

    acc_token = create_token(
        data={"sub": user.id, "email": user.email},
    )
    refresh_token = create_token(
        data={"sub": user.id, "email": user.email, "refresh": True}
    )
    return {"acc_token": acc_token, "refresh_token": refresh_token}
