from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Request, status

from app.helpers.get_database import get_database
from app.helpers.create_decode_tokens import create_token
from app.helpers.validate_tokens import validate_access_token, validate_refresh_token


async def get_user_from_cookies(
    request: Request, response: Response, db=Depends(get_database)
):
    """Retrieve user from access or refresh tokens in cookies if no access token found, try refresh token"""

    if not request.cookies:
        raise HTTPException(
            status_code=401, detail="No cookies found, redirect to login"
        )
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if access_token:
        try:
            user = await validate_access_token(access_token, db)
            print("User found in access token")
            return user
        except HTTPException as e:
            if e.status_code == 401 and refresh_token:
                print("Access token expired, trying refresh token")

    if refresh_token:
        try:
            user = await validate_refresh_token(refresh_token, db)
            new_access_token = create_token(
                data={"sub": user["_id"], "email": user["email"]}, expire_time=1200
            )
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite="lax",
            )
            return user
        except HTTPException as e:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token, redirect to login"
            )
    raise HTTPException(status_code=401, detail="No valid token found")
