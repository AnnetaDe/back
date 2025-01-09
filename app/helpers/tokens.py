from datetime import timedelta
from typing import Optional

from datetime import datetime

import os

from fastapi import Depends, HTTPException, status
from fastapi import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.routes.auth.login import get_database, get_user_by_id

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = os.getenv("ALGORITHM")
if ALGORITHM is None:
    raise ValueError("ALGORITHM environment variable is not set")
else:
    ALGORITHM = str(ALGORITHM)


def create_token(data: dict, expire_time: Optional[int] = 1200):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expire_time or 30)
    to_encode.update({"exp": expire})
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY environment variable is not set")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY environment variable is not set")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[str(ALGORITHM)])

        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")


security = HTTPBearer()


def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        user = get_user_by_id(user_id, db=Depends(get_database))
        if user is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return user
