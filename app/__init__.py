from fastapi import Depends, FastAPI, HTTPException

from app.db.database import start_database
import os
from dotenv import load_dotenv
from app.routes.auth.register import register_router
from app.routes.auth.login import get_current_user, login_router
from app.routes.auth.tests import test_router


load_dotenv()


app = FastAPI()
if os.getenv("DEBUG", "false") == "true" or os.getenv("DEBUG", "false") == "1":
    app.debug = True
else:
    app.debug = False
# app.add_middleware(CORS, expose_headers=["Authorization"], allow_credentials=True)
# CORS(app, expose_headers="Authorization", allow_credentials=True)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(register_router, prefix="", tags=["Register"])
app.include_router(login_router, prefix="", tags=["Login"])
app.include_router(
    test_router, prefix="", tags=["Test"], dependencies=[Depends(get_current_user)]
)


@app.get("/users")
def read_users():
    try:
        db = start_database()
        # Check database connection with a ping
        db.client.admin.command("ping")
        users_collection = db["users"]

        users = list(users_collection.find({}, {"_id": 0}))
        return {
            "status": "success",
            "message": "Database connection is active",
            "data": users,
        }
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail="Database connection failed",
            headers={"X-Error": str(e)},
        )
