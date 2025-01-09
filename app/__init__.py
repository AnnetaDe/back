from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import close_database, start_database
from dotenv import load_dotenv
from app.routes.auth.login import get_current_user, login_router
from app.routes.auth.tests import test_router
from app.routes.other.public import public_router


load_dotenv()


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = None
    try:
        client = await start_database()
        app.state.db = client["studapp"]
        print(" MongoDB is connected")
        yield
    finally:
        if client is not None:
            await close_database(client)
            print("Closed MongoDB connection")


app = FastAPI(lifespan=lifespan)
origins = [
    "http://192.168.1.73:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def start():
    return {"message": "Explore the services"}


app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(test_router, prefix="/test", tags=["Test"])
app.include_router(public_router, prefix="/public", tags=["Public"])
