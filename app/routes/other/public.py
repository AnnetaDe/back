from fastapi import APIRouter, Depends

from app.helpers.hide_answer import hide_answer
from app.routes.auth.login import get_database


public_router = APIRouter()


@public_router.get(
    "/pool",
)
async def get_pool(db=Depends(get_database)):
    """
    Retrieve the test generation history for the authenticated user.
    """
    pool = await db["pool"].find().to_list(length=100)
    return hide_answer(pool)
