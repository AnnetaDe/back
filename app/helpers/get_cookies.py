from fastapi import FastAPI, Cookie, HTTPException, Depends

from app.helpers.tokens import decode_token


def get_cookies(
    access_token: str | None = Cookie(None), refresh_token: str | None = Cookie(None)
):
    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Missing tokens in cookies")

    print("Cookies:im here")

    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    decoded_access_token = decode_token(access_token)
    decoded_refresh_token = decode_token(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}
