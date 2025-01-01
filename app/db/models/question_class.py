import hashlib
from faker import Faker
from pydantic import BaseModel, Field, EmailStr, field_validator, validator
from typing import Optional, Dict
from pymongo.database import Database

fake = Faker()


class Question(BaseModel):
    id: Optional[str] = Field(alias="_id")
    question: str = Field(alias="question")
    choices: dict[str, str] = Field(alias="choices")
    subject: str = Field(alias="subject")
    answer: str = Field(alias="answer")
    level: Optional[str] = Field(alias="level")
    hash: Optional[str] = Field(alias="hash")

    @staticmethod
    def generate_hash(question_text: str) -> str:
        """
        Generate a SHA-256 hash for the question text.
        """
        return hashlib.sha256(question_text.encode("utf-8")).hexdigest()

    def check_uniq_save_to_db(
        self, db: Database, collection_name: str = "questions"
    ) -> bool:
        """
        Save the question to the database after ensuring uniqueness.
        """

        existing_question = db[collection_name].find_one({"hash": self.hash})
        if existing_question:
            return False

        db[collection_name].insert_one(self.model_dump(by_alias=True))
        print("Question saved successfully.")
        return True

    @classmethod
    def create_question(
        cls,
        question: str,
        choices: Dict[str, str],
        subject: str,
        level: int,
        answer: str,
        hash: Optional[str] = None,
    ) -> "Question":
        """
        Create a new question instance.

        """
        question_hash = cls.generate_hash(question)

        return cls(
            _id=str(fake.uuid4()),
            question=question,
            choices=choices,
            subject=subject.capitalize(),
            level=str(level),
            answer=answer,
            hash=hash,
        )

    class Config:
        populate_by_name = True
