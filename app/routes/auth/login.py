from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import jwt

from app.db import database
from app.db.models.user import User
from app.helpers.tokens import create_token, decode_token
from app.helpers.get_current_user import get_current_user


login_router = APIRouter()
databaseU = database.start_database()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class Token_data(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str


class UserLoginRequest(BaseModel):
    username: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class ProfileResponse(BaseModel):
    user_id: str
    email: str


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str
    role: str
    verified: bool
    performance: int
    avatar: str


@login_router.post("/login", response_model=UserLoginResponse)
async def api_login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response
):

    user = User.verify_user_email_password(
        email=form_data.username, password=form_data.password, db=databaseU
    )

    if not user or user.id is None:
        return HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    acc_token = create_token(
        data={"sub": user.id, "email": user.email},
        expire_time=30,
    )
    refresh_token = create_token(
        data={"sub": user.id, "email": user.email, "refresh": True},
        expire_time=1200,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {acc_token}",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {
        "access_token": acc_token,
        "refresh_token": refresh_token,
    }


@login_router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):

    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Missing refresh token.Please login"
        )
    try:
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload["sub"]
        user = User.get_user_by_id(user_id=user_id, db=databaseU)
        if not user:
            raise HTTPException(
                status_code=401, detail="Broken token, user id not found"
            )

        # Generate a new access token
        new_acc_token = create_token(
            data={"sub": payload["sub"], "email": payload["email"]}, expire_time=30
        )
        new_refresh_token = create_token(
            data={"sub": payload["sub"], "email": payload["email"], "refresh": True},
            expire_time=1200,
        )
        user.update_refresh_token(
            user_id=user_id, refresh_token=new_refresh_token, db=databaseU
        )
        response.set_cookie(
            key="access_token",
            value=new_acc_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return {
            "access_token": new_acc_token,
            "refresh_token": new_refresh_token,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@login_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@login_router.get("/profile")
async def get_user_profile(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "performance": current_user.performance,
        "avatar": current_user.avatar,
        "verified": current_user.verified,
    }
