from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
import jwt
from jwt import PyJWTError

from app.db.models.performance import Performance
from app.db.models.user import User
from app.helpers.tokens import create_token, decode_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_database(request: Request):
    return request.app.state.db


async def get_current_user(
    encrypted_token=Depends(oauth2_scheme), db=Depends(get_database)
):
    try:
        payload = decode_token(encrypted_token)
        current_user_id: str = payload.get("sub")
        if not current_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        current_user = await get_user_by_id(current_user_id, db)
        current_user = User(**current_user)

        return current_user
    except PyJWTError as e:
        raise HTTPException(
            status_code=401, detail="Something went wrong with the token"
        )


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


async def get_user_by_id(user_id: str, db):
    user = await db["users"].find_one({"_id": user_id})
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


@login_router.post("/login")
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db=Depends(get_database),
):
    user = await verify_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    acc_token = create_token(
        data={"sub": user["_id"], "email": user["email"]},
        expire_time=120,
    )
    refresh_token = create_token(
        data={"sub": user["_id"], "email": user["email"], "refresh": True},
        expire_time=1200,
    )

    response.set_cookie(
        key="access_token",
        value=acc_token,
        httponly=True,
        secure=True,
        samesite="none",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
    )

    return user


@login_router.post("/refresh")
async def refresh_token(
    response: Response, refresh_token: str = Cookie(None), db=Depends(get_database)
):

    if not refresh_token:
        raise HTTPException(
            status_code=401, detail="Missing refresh token.Please login"
        )
    try:
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload["sub"]
        new_refresh_token = create_token(
            data={"sub": payload["sub"], "email": payload["email"], "refresh": True},
            expire_time=1200,
        )
        await update_refresh_token(user_id, new_refresh_token, db)

        # Generate a new access token
        new_acc_token = create_token(
            data={"sub": payload["sub"], "email": payload["email"]}, expire_time=30
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
        return "Token refreshed successfully"
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
async def get_user_profile(
    Request,
    current_user: CurrentUser = Depends(get_current_user),
):

    return current_user
