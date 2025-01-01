from datetime import datetime
from faker import Faker
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.db.database import start_database
from app.db.make_test import generate_test
from app.helpers.get_current_user import get_current_user
from app.helpers.hide_answer import hide_answer, show_answer
from app.db.models.performance import Performance, TestPerformance

test_router = APIRouter()
database = start_database()


class TestRequest(BaseModel):
    subject: str
    number_of_questions: int
    level: int


class TestResponse(BaseModel):
    test_id: str
    message: str
    status: str
    level: int
    subject: str
    test_data: list[dict]
    completed: bool
    date: str


class TestSubmission(BaseModel):
    test_id: str
    selected_answers: list[int]


class Scores(BaseModel):
    status: dict
    message: str


class CompletedResponse(BaseModel):
    history: list[dict]


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str
    role: str
    verified: bool
    performance: int


fake = Faker()


@test_router.post("/test", response_model=TestResponse)
async def generate(
    data: TestRequest, current_user: CurrentUser = Depends(get_current_user)
):
    """Generate a test."""

    user_id = current_user.id
    _id = str(fake.uuid4())

    questions = generate_test(
        subject=data.subject,
        number_of_questions=data.number_of_questions,
        level=data.level,
    )
    if not questions:
        raise HTTPException(status_code=400, detail="Error generating test")
    hidden_answers = [
        {
            "question": q["question"],
            "choices": q["choices"],
            "submit_answer": hide_answer(q["answer"]),
        }
        for q in questions
    ]
    bd = start_database()
    bd["history"].insert_one(
        {
            "_id": _id,
            "user_id": user_id,
            "subject": data.subject,
            "level": data.level,
            "test_data": hidden_answers,
            "completed": False,
            "timestamp": datetime.now(),
        }
    )

    return {
        "test_id": _id,
        "status": "success",
        "message": "Test created",
        "subject": data.subject,
        "level": data.level,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_data": hidden_answers,
        "completed": False,
    }


@test_router.post("/submit-answers", response_model=Scores)
async def submit_answers(
    test_data: TestSubmission,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Submit answers for a test and evaluate correctness.
    """
    db = start_database()
    user_id = current_user.id
    performance_board_id = current_user.performance
    test_id = test_data.test_id

    if not performance_board_id:
        user_performance = Performance.create_performance(user_id)
        user_performance.save_to_db(db, collection_name="performance_board")
        db["users"].update_one(
            {"_id": user_id}, {"$set": {"performance": user_performance.id}}
        )
    selected_answers = test_data.selected_answers
    if not selected_answers:
        raise HTTPException(status_code=400, detail="No answers submitted")
    test_to_evaluate = db["history"].find_one({"_id": test_id})
    if test_to_evaluate is None:
        raise HTTPException(status_code=404, detail="Test not found")
    current_subject = test_to_evaluate["subject"]
    current_level = test_to_evaluate["level"]
    if test_to_evaluate is None:
        raise HTTPException(status_code=404, detail="Test not found")
    if test_to_evaluate["completed"] == True:
        raise HTTPException(status_code=400, detail="Test already completed")
    if len(selected_answers) < len(test_to_evaluate["test_data"]):
        selected_answers.extend(
            [0] * (len(test_to_evaluate["test_data"]) - len(selected_answers))
        )
    if len(selected_answers) > len(test_to_evaluate["test_data"]):
        selected_answers = selected_answers[: len(test_to_evaluate["test_data"])]
    is_correct = 0
    total_num_questions = len(test_to_evaluate["test_data"])

    for question, selected_answer in zip(
        test_to_evaluate["test_data"], selected_answers
    ):
        question["submitted_answer"] = selected_answer
        question["correct_answer"] = int(show_answer(question["submit_answer"]))
        question["is_correct"] = (
            int(show_answer(question["submit_answer"])) == selected_answer
        )
        is_correct += int(question["is_correct"])
        del question["submit_answer"]

    current_test_summary = TestPerformance.create_test_summary(
        test_id=test_id,
        subject=current_subject,
        level=current_level,
        correct_answers=is_correct,
        num_test_questions=total_num_questions,
        score=int(is_correct / total_num_questions * 100),
        completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    Performance.update_tests(
        performance_id=str(performance_board_id),
        test=current_test_summary,
        db=db,
        collection_name="performance_board",
    )
    db["history"].update_one(
        {"_id": test_id},
        {"$set": {"completed": True, "test_data": test_to_evaluate["test_data"]}},
    )

    return {
        "status": {
            "test": test_id,
            "correct": is_correct,
            "incorrect": total_num_questions - is_correct,
            "score_%": is_correct / total_num_questions * 100,
        },
        "message": "amazing",
    }


@test_router.get("/completed", response_model=CompletedResponse)
async def get_user_history(current_user: CurrentUser = Depends(get_current_user)):
    """
    Retrieve the test generation history for the authenticated user.
    """
    user_id = current_user.id
    db = start_database()

    history = list(db["history"].find({"user_id": user_id}))

    return {"history": history}
