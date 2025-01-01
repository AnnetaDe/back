from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, field_validator

from app.db.database import start_database
from app.db.models.user import User


register_router = APIRouter()
database = start_database()


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

    @field_validator("password")
    def validate_password(cls, password):
        if len(password) < 2:
            raise ValueError("Password must be at least 2 characters long")
        return str(password)

    @field_validator("name")
    def validate_name(cls, name):
        if len(name.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return name


@register_router.post("/register")
async def api_create_user(data: UserCreateRequest):
    """Register a new user."""
    if User.email_exists(email=data.email, db=database):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create a new user
    new_user = User.create_user(
        role=data.role,
        name=data.name,
        email=data.email,
        password=data.password,
    )

    # Save the user to the database
    try:
        new_user.save_to_db(db=database)
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB error")

    # Return success response (exclude sensitive fields like password)
    return {
        "status": "success",
        "message": "User created successfully",
        "data": new_user.model_dump(by_alias=True, exclude={"password"}),
    }
