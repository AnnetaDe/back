from fastapi import FastAPI, Cookie, HTTPException, Depends


def get_cookies(
    access_token: str | None = Cookie(None), refresh_token: str | None = Cookie(None)
):
    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Missing tokens in cookies")

    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")

    return {"access_token": access_token, "refresh_token": refresh_token}
