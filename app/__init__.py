import logging
from fastapi import FastAPI, HTTPException
from bson import ObjectId

from app.db.models import user
from app.db.database import start_database
import os
from fastapi.middleware.cors import CORSMiddleware as CORS
from dotenv import load_dotenv
from app.routes.api.auth.register import register_router
from app.routes.api.auth.login import login_router


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
        logging.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
