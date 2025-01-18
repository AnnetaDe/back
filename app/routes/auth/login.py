from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status

from fastapi import security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator

from jwt import PyJWTError
import datetime

from app.db.models.performance import Performance
from app.db.models.user import User

from app.helpers.get_user_from_cookies import get_user_from_cookies
from app.helpers.create_decode_tokens import create_token, decode_token
from app.helpers.get_database import get_database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login", scopes={"me": "Read information about the current user."}
)


class UserLoginRequest(BaseModel):
    username: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    user: dict


class ProfileResponse(BaseModel):
    user: dict


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str
    role: str
    verified: bool
    performance: int
    avatar: str


class UserRegister(BaseModel):
    username: EmailStr
    password: str
    name: str


async def insert_user_to_db(user, db, collection):

    return await db[collection].insert_one(user.model_dump(by_alias=True))


async def check_user_exists(email: str, db):
    user = await db["users"].find_one({"email": email})
    return user


async def verify_user(email: str, password: str, db):
    user = await db["users"].find_one({"email": email})
    if not user:
        return False
    if not pwd_context.verify(password, user["password"]):
        return False
    return user


async def update_refresh_token(user_id: str, refresh_token: str, db):
    await db["users"].update_one(
        {"_id": user_id}, {"$set": {"refresh_token": refresh_token}}
    )
    return "Refresh token updated successfully"


login_router = APIRouter()


@login_router.post("/register")
async def create_user(data: UserRegister, db=Depends(get_database)):

    try:
        user = await check_user_exists(data.username, db)
        if user:
            return HTTPException(
                status_code=400,
                detail="You already have an account. Please login",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB error")

    new_user = User.create_user(
        name=data.name,
        email=data.username,
        password=data.password,
        role="student",
        verified=False,
    )
    user_performance = Performance.create_performance(
        user_id=new_user.id if new_user.id else "",
        performance_id=new_user.performance if new_user.performance else "",
    )
    await db["performance_board"].insert_one(user_performance.model_dump())
    await insert_user_to_db(new_user, db, "users")

    return "User created successfully"


@login_router.post("/login", response_model=UserLoginResponse)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db=Depends(get_database),
):
    user = await verify_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    acc_token = create_token(data={"sub": user["_id"], "email": user["email"]})
    refresh_token = create_token(
        data={"sub": user["_id"], "email": user["email"], "refresh": True},
    )

    decoded_a = decode_token(acc_token)
    decoded_r = decode_token(refresh_token)

    exp_a = datetime.datetime.fromtimestamp(decoded_a["exp"]).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    exp_r = datetime.datetime.fromtimestamp(decoded_r["exp"]).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    await update_refresh_token(user["_id"], refresh_token, db)
    response.headers["WWW-authentificate"] = f"Bearer {acc_token}"

    # response.headers.update(
    #     {
    #         "Set-Cookie": f"access_token={acc_token}; HttpOnly; Secure; SameSite=None; Expires={exp_a};",
    #         "Set-Cookie": f"refresh_token={refresh_token}; HttpOnly; Secure; SameSite=None; Expires={exp_r};",
    #     }
    # )

    response.set_cookie(
        key="access_token",
        value=acc_token,
        httponly=True,
        secure=True,
        samesite="lax",
        expires=exp_a,
        max_age=600,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        expires=exp_r,
        max_age=86400,
        path="/",
    )

    return {"user": user}


@login_router.get("/me", response_model=ProfileResponse)
async def get_profile(
    current_user: Annotated[dict, Depends(get_user_from_cookies)],
):
    if current_user is None:
        raise HTTPException(
            status_code=401, detail="user not authenticated or not found"
        )
    return {"user": current_user}


@login_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
