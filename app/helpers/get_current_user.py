from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
import os
from app.db.models.user import User
from app.helpers.tokens import decode_token
from app.db.models.user import User
from app.db.database import start_database


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
database = start_database()


def get_current_user(encrypted_token: str = Depends(oauth2_scheme)):

    try:
        payload = decode_token(encrypted_token)
        current_user_id = payload.get("sub")
        if not current_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        current_user = User.get_user_by_id(
            user_id=current_user_id, db=database, collection_name="users"
        )
        if not current_user:

            raise HTTPException(status_code=401, detail="User not found")
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="User ID is None")

        return current_user
    except PyJWTError as e:
        raise HTTPException(
            status_code=401, detail="Something went wrong with the token"
        )
