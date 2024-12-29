from faker import Faker
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from enum import Enum
import datetime
from pymongo.database import Database
from app.helpers.hashed import hash_password, verify_password


fake = Faker()


class User(BaseModel):
    id: Optional[str] = Field(alias="_id")

    role: str = Field(alias="role")
    name: str = Field(alias="name")
    email: EmailStr = Field(alias="email")
    password: str = Field(alias="password")
    verified: bool = Field(alias="verified", default=False)
    date_created: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, alias="date_created"
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

    @staticmethod
    def create_user(
        name: str,
        email: EmailStr,
        password: str,
        role: str,
        verified: bool = False,
    ) -> "User":
        """Create a new user instance."""
        return User(
            _id=str(fake.uuid4()),
            name=name,
            email=email.lower(),
            password=hash_password(password),
            role=role,
            verified=verified,
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

    class Config:
        populate_by_name = True
