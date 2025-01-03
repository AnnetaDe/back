import hashlib
from uuid import uuid4
from faker import Faker
from pydantic import BaseModel, Field, EmailStr, field_validator, validator
from typing import Literal, Optional, Dict
from pymongo.database import Database

from app.helpers.uniq_id import unique_id


class Question(BaseModel):
    id: str = Field(default_factory=lambda: unique_id("qu"), alias="_id")
    question: str
    choices: Dict[Literal["1", "2", "3", "4"], str]
    subject: str
    answer: Literal["1", "2", "3", "4"]
    level: int
    hash: Optional[str] = Field(alias="hash", default=None)
    is_hidden: bool = Field(default=True, exclude=True)

    @classmethod
    def create_question(cls, dict_data, hashed) -> "Question":
        """
        Parse the JSON response from GPT into a Question instance.

        :param json_data: The JSON response from GPT.
        :return: A Question instance.

        """
        cls.model_validate(dict_data)
        return cls(
            question=dict_data["question"],
            choices=dict_data["choices"],
            subject=dict_data["subject"],
            answer=dict_data["answer"],
            level=dict_data["level"],
            hash=hashed,
        )

    def populate_by_field(self, name: str):
        self.name = name
        return self
