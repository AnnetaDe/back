async def get_user_by_id(user_id: str, db):
    user = await db["users"].find_one({"_id": user_id})
    return user
