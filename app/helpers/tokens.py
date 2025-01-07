from datetime import timedelta
from typing import Optional

from datetime import datetime

import os

import jwt

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
