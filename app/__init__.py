from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

from app.db.database import close_database, start_database
from dotenv import load_dotenv
from app.routes.auth.login import get_current_user, login_router
from app.routes.auth.tests import test_router


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


@app.get("/")
def start():

    return {"message": "Hello StudApp"}


app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(
    test_router, prefix="", tags=["Test"], dependencies=[Depends(get_current_user)]
)
