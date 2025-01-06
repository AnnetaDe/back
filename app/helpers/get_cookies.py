from fastapi import FastAPI, Cookie, HTTPException, Depends

app = FastAPI()


def extract_tokens(
    access_token: str | None = Cookie(None), refresh_token: str | None = Cookie(None)
):
    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Missing tokens in cookies")

    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")

    return {"access_token": access_token, "refresh_token": refresh_token}


# @app.post("/test/generate")
# async def generate(data: dict, tokens=Depends(extract_tokens)):
#     return {
#         "message": "Tokens processed successfully",
#         "access_token": tokens["access_token"],
#         "refresh_token": tokens["refresh_token"],
#     }
