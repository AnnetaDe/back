from datetime import datetime
from faker import Faker
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional


from app.db.make_test import generate_test
from app.helpers.hide_answer import hide_answer, show_answer
from app.db.models.performance import Performance, TestPerformance
from app.routes.auth.login import get_current_user, get_user_by_id

test_router = APIRouter()
fake = Faker()


async def get_database(request: Request):
    return request.app.state.db


class TestRequest(BaseModel):
    subject: str
    count: int
    level: int


class TestResponse(BaseModel):
    test_id: str
    message: str
    status: str
    level: int
    subject: str
    test_data: list[dict]
    completed: bool
    count: int
    date: str


class TestSubmission(BaseModel):
    test_id: str
    selected_answers: list[int]
    user_id: Optional[str] = None


class Scores(BaseModel):
    status: dict


class CompletedResponse(BaseModel):
    history: list[dict]


class CurrentUser(BaseModel):
    id: str
    email: str
    name: str
    role: str
    verified: bool
    performance: str
    history: str


class GetPerformance(BaseModel):
    user_id: str


@test_router.post("/generate", response_model=TestResponse)
async def generate(
    data: TestRequest,
    db=Depends(get_database),
    # current_user: CurrentUser = Depends(get_current_user),
):
    """Generate a test."""
    # user_id = current_user.id
    _id = str(fake.uuid4())

    questions = await generate_test(
        subject=data.subject,
        number_of_questions=data.count,
        level=data.level,
        db=db,
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

    await db["history"].insert_one(
        {
            "_id": _id,
            # "user_id": user_id,
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
        "count": len(hidden_answers),
        "subject": data.subject,
        "level": data.level,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_data": hidden_answers,
        "completed": False,
    }


@test_router.post("/submit-answers", response_model=Scores)
async def submit_answers(
    test_data: TestSubmission,
    # current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Submit answers for a test and evaluate correctness.
    """

    test_id = test_data.test_id
    selected_answers = test_data.selected_answers
    if not selected_answers:
        raise HTTPException(status_code=400, detail="No answers submitted")
    test_to_evaluate = await db["history"].find_one({"_id": test_id})
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

    if test_data.user_id is not None:
        user_id = test_data.user_id
        print(user_id)
        if user_id is None:
            raise HTTPException(status_code=400, detail="User ID is required")

        user = await get_user_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        board_id = user["performance"]
        hisoty_id = user["history"]
        print(board_id, hisoty_id)

        await db["history"].update_one(
            {"_id": test_id},
            {"$set": {"completed": True, "test_data": test_to_evaluate["test_data"]}},
        )

        await db["performance_board"].update_one(
            {"board_id": board_id},
            {
                "$push": {"tests": current_test_summary.model_dump()},
                "$inc": {
                    "total_tests": 1,
                    "total_score": int(is_correct / total_num_questions * 100),
                    "total_questions": total_num_questions,
                    f"total_by_subj.{current_subject}": 1,
                    f"total_by_level.{current_level}": 1,
                },
            },
        )

    return {
        "status": {
            "test": test_id,
            "correct": is_correct,
            "incorrect": total_num_questions - is_correct,
            "score": is_correct / total_num_questions * 100,
            "completed": True,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "message": "amazing",
    }


@test_router.get("/history")
async def get_user_history(user_id: str = Query(...), db=Depends(get_database)):
    """
    Retrieve the test generation history for the authenticated user.
    """
    history = await db["history"].find({"user_id": user_id}).to_list(length=100)

    return {"history": history}


@test_router.get("/performance")
async def get_user_performance(user_id: str = Query(...), db=Depends(get_database)):
    """
    Retrieve the test generation history for the authenticated user.

    """
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID is required")

    user = await get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    board_id = user["performance"]
    performance = await db["performance_board"].find_one({"board_id": board_id})
    if performance is None:
        raise HTTPException(status_code=404, detail="Performance board not found")
    print(performance)
    if "_id" in performance:
        performance["_id"] = str(performance["_id"])

    return {"user_id": user_id, "performance": performance}
