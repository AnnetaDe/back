from dbm import dumb
from pyexpat import model
from faker import Faker
from pydantic import BaseModel, Field
from typing import Dict, Optional
from pymongo.database import Database


fake = Faker()


class TestPerformance(BaseModel):
    test_id: str
    test_subject: str
    test_level: int
    correct_answers: int
    num_test_questions: int
    test_score: int
    completed_at: str

    @classmethod
    def create_test_summary(
        cls,
        test_id: str,
        subject: str,
        level: int,
        correct_answers: int,
        num_test_questions: int,
        score: int,
        completed_at: str,
    ):
        new_test_perf = cls(
            test_id=test_id,
            test_subject=subject,
            test_level=level,
            correct_answers=correct_answers,
            num_test_questions=num_test_questions,
            test_score=score,
            completed_at=completed_at,
        )
        return new_test_perf


class Performance(BaseModel):
    board_id: Optional[str] = Field(alias="board_id")
    user_id: str
    tests: list[TestPerformance]
    total_score: int
    total_tests: int
    total_questions: int
    total_by_subj: Dict[str, int]
    total_by_level: Dict[int, int]

    @classmethod
    def create_performance(cls, user_id: str, performance_id: str):
        return cls(
            board_id=performance_id,
            user_id=user_id,
            tests=[],
            total_score=0,
            total_tests=0,
            total_questions=0,
            total_by_subj={},
            total_by_level={},
        )

    class Config:

        populate_by_alias = True
        json_schema_extra = {
            "example": {
                "board_id": "123",
                "user_id": "123",
                "tests": [
                    {
                        "test_id": "123",
                        "test_subject": "Math",
                        "test_level": 1,
                        "correct_answers": 10,
                        "num_test_questions": 10,
                        "test_score": 100,
                        "completed_at": "2021-01-01 12:00:00",
                    }
                ],
                "total_score": 100,
                "total_tests": 1,
                "total_questions": 10,
                "total_by_subj": {"Math": 1},
                "total_by_level": {1: 1},
            }
        }
