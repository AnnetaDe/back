from faker import Faker
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from enum import Enum
import datetime
from pymongo.database import Database
from app.db.models.performance import Performance
from app.helpers.hashed import hash_password, verify_password


fake = Faker()


class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    performance: Optional[str] = Field(alias="performance")

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

    @classmethod
    def create_user(
        cls,
        name: str,
        email: EmailStr,
        password: str,
        role: str,
        verified: bool = False,
        refresh_token: Optional[str] = None,
        performance: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> "User":
        """Create a new user instance."""
        return cls(
            _id=str(fake.uuid4()),
            name=name,
            email=email.lower(),
            password=hash_password(password),
            role=role,
            verified=verified,
            refresh_token=refresh_token,
            performance=performance,
            avatar=avatar,
        )

    def save_to_db(self, db: Database, collection_name: str = "users"):
        """Save the user instance to a collection in db."""
        db[collection_name].insert_one(self.model_dump(by_alias=True))

    @staticmethod
    def email_exists(email: str, db: Database, collection_name: str = "users") -> bool:
        """Check if email exists in the database."""
        return db[collection_name].find_one({"email": email.lower()}) is not None

    @staticmethod
    def find_by_email(
        email: str, db: Database, collection_name: str = "users"
    ) -> Optional["User"]:
        """Find a user by email in the db."""
        data = db[collection_name].find_one({"email": email.lower()})
        return User(**data) if data else None

    @staticmethod
    def verify_user_email_password(
        email: str, password: str, db: Database, collection_name: str = "users"
    ) -> Optional["User"]:
        """Verify  password and email."""
        user = User.find_by_email(email=email, db=db, collection_name=collection_name)
        if not user:
            return
        if verify_password(password, user.password):
            return User(**user.model_dump())

    @staticmethod
    def get_user_by_id(user_id: str, db: Database, collection_name: str = "users"):
        """Get a user by id."""
        data = db[collection_name].find_one({"_id": user_id})
        return User(**data) if data else None

    @staticmethod
    def update_refresh_token(
        user_id: str, refresh_token: str, db: Database, collection_name: str = "users"
    ):
        """Update the refresh token for a user."""
        result = db[collection_name].update_one(
            {"_id": user_id}, {"$set": {"refresh_token": refresh_token}}
        )
        if result.matched_count == 0:
            raise ValueError(f"User with ID {user_id} not found.")

    @staticmethod
    def update_user(
        user_id: str, data: dict, db: Database, collection_name: str = "users"
    ):
        """Update the user details."""
        result = db[collection_name].update_one({"_id": user_id}, {"$set": data})
        if result.matched_count == 0:
            raise ValueError(f"User with ID {user_id} not found.")

    class Config:
        populate_by_name = True
