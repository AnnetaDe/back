import hashlib
import os
from pprint import pprint
from uuid import uuid4
from typing import Optional

from app.db.models.question_class import Question
from app.db.models.gpt_handler_class import GPTHandler

import json


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_TOKENS = 100
TEMPERATURE = 0.9
MODEL = "gpt-3.5-turbo"
DEFAULT_MODEL = "gpt-2"
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")


gpt_handler = GPTHandler(
    api_key=OPENAI_API_KEY,
    model=MODEL,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE,
)


def parse_gpt_response(raw_response: str) -> Optional[dict]:
    try:
        # Attempt to parse the JSON
        parsed = json.loads(raw_response)
        return parsed
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print("Raw response:", raw_response)
        return None


def hashed(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


async def generate_test(subject, number_of_questions, level, db):
    """
    Generate multiple-choice questions about a given subject using GPT-3.5.

    :param subject: The subject for the questions.
    :param number_of_questions: The number of questions to generate.
    :return: A list of generated questions.
    """
    if number_of_questions < 1:
        raise ValueError("Number of questions must be at least 1.")
    if number_of_questions > 25:
        number_of_questions = 25

    questions = []
    existing = (
        await db["questions"]
        .find({"subject": subject, "level": level})
        .to_list(number_of_questions)
    )

    questions.extend(existing)
    remaining_questions = (
        number_of_questions - len(existing)
        if len(existing) < number_of_questions
        else 0
    )

    MAX_RETRIES = 25
    attempts = 0
    while remaining_questions > 0 and attempts < MAX_RETRIES:
        try:
            attempts += 1
            # Generate a new question
            new_question_data = await gpt_handler.generate_question(
                subject=subject, level=level
            )
            if new_question_data:
                parsed_answer = parse_gpt_response(new_question_data)
                if not parsed_answer:
                    print("Error parsing GPT response, skipping.")
                    continue
                new_instance = Question.create_question(
                    parsed_answer, hashed(parsed_answer["question"])
                )

                if new_instance:
                    not_unique = await db["questions"].find_one(
                        {"hash": new_instance.hash}
                    )
                    print("Checking for uniqueness...")
                    if not_unique:
                        attempts += 1
                        print("Question already exists, skipping.")
                        continue

                    await db["questions"].insert_one(
                        new_instance.model_dump(by_alias=True)
                    )
                    print("New question added successfully.")

                    questions.append(new_instance.model_dump())
                    remaining_questions -= 1

        except Exception as e:
            print(f"Error generating or saving question: {e}")
            break
    return questions
