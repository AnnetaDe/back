import datetime
from fastapi import Request, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from app.helpers.get_user_by_id import get_user_by_id
from app.helpers.create_decode_tokens import decode_token


async def validate_access_token(token: str, db):
    """Validate and decode the access token. return user"""
    try:
        decoded_token = decode_token(token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid access token")
        user_id = decoded_token["sub"]
        if not "sub" or not "exp" in decoded_token:
            raise HTTPException(
                status_code=401, detail="Invalid user or exp in access token"
            )
        expired = decoded_token["exp"]
        if expired < int(datetime.datetime.now().timestamp()):
            raise HTTPException(status_code=401, detail="Access token expired")
        user = await get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")


async def validate_refresh_token(refresh_token: str, db):
    """ " Validate and decode the refresh token. return user"""
    try:
        decoded_token = decode_token(refresh_token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = decoded_token["sub"]
        if not "sub" or not "exp" in decoded_token:
            raise HTTPException(
                status_code=401, detail="Invalid user or exp in refresh token"
            )
        user = await get_user_by_id(user_id, db)

        if not user or user["refresh_token"] != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
