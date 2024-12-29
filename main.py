import os
import uvicorn
from app import app
from app.helpers.setup_logger import setup_logging


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    setup_logging()
    uvicorn.run("app:app", port=port, reload=debug)


# @app.get("/users", response_model=list)
# def serialize_user(user):
#     return {
#         "id": str(user["_id"]),
#         "name": user["name"],
#         "email": user["email"],
#         "age": user["age"],
#     }


# @app.post("/users", response_model=dict)
# async def create_user(user: user.User):
#     user_data = user.dict()
#     user_data["hashed_password"] = user_data["hashed_password"]
#     result = db.users.insert_one(user_data)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return serialize_user(user)
