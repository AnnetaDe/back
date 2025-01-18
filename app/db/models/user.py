from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from enum import Enum
import datetime
from pymongo.database import Database
from app.db.models.performance import Performance
from app.helpers.hash_verify_password import hash_password, verify_password
from app.helpers.uniq_id import unique_id


class User(BaseModel):
    id: Optional[str] = Field(
        alias="_id", default_factory=lambda: unique_id(prefix="user")
    )
    performance: Optional[str] = Field(
        alias="performance", default_factory=lambda: unique_id(prefix="perf")
    )
    history: Optional[str] = Field(
        alias="history", default_factory=lambda: unique_id(prefix="hist")
    )

    role: str = Field(alias="role")
    name: str = Field(alias="name")
    email: EmailStr = Field(alias="email")
    password: str = Field(alias="password")
    verified: bool = Field(alias="verified", default=False)
    refresh_token: Optional[str] = Field(alias="refresh_token")
    avatar: Optional[str] = Field(alias="avatar")
    date_created: datetime.datetime = Field(
        default_factory=datetime.datetime.now, alias="date_created"
    )

    @field_validator("password")
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

    @field_validator("name")
    def validate_name(cls, name):
        if len(name.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return name

    @field_validator("email")
    def validate_email(cls, email):
        if len(email.strip()) == 0:
            raise ValueError("Email cannot be empty")
        return email

    @classmethod
    def create_user(
        cls,
        name: str,
        email: EmailStr,
        password: str,
        role: str,
        verified: bool = False,
        refresh_token: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> "User":
        """Create a new user instance."""
        return cls(
            name=name,
            email=email.lower(),
            password=hash_password(password),
            role=role,
            verified=verified,
            refresh_token=refresh_token,
            avatar=avatar,
        )

    class Config:
        populate_by_name = True
