import hashlib
import os

from app.db.models.question_class import Question
from app.db.models.gpt_handler_class import GPTHandler
from app.db.database import start_database
import json


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_TOKENS = 100
TEMPERATURE = 0.8
MODEL = "gpt-3.5-turbo"
DEFAULT_MODEL = "gpt-4"
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set")


gpt_handler = GPTHandler(
    api_key=OPENAI_API_KEY,
    model=MODEL,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE,
)


def parse_gpt_response(raw_response):
    try:
        # Attempt to parse the JSON
        parsed = json.loads(raw_response)
        return parsed
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print("Raw response:", raw_response)
        return None


def generate_test(subject, number_of_questions, level):
    """
    Generate multiple-choice questions about a given subject using GPT-3.5.

    :param subject: The subject for the questions.
    :param number_of_questions: The number of questions to generate.
    :return: A list of generated questions.
    """
    db = start_database()

    questions = []
    result = list(
        db["questions"]
        .find({"$and": [{"subject": subject.capitalize()}, {"level": str(level)}]})
        .limit(number_of_questions)
    )
    questions.extend(result)

    remaining_questions = (
        number_of_questions - len(result) if len(result) < number_of_questions else 0
    )
    print(f"Questions already present: {len(questions)}")
    print(f"Questions to generate: {remaining_questions}")

    while remaining_questions > 0:
        try:
            # Generate a new question
            new_question_data = gpt_handler.generate_question(
                subject=subject, level=level
            )
            parsed_question = parse_gpt_response(new_question_data)

            if parsed_question:
                # Create a Question instance
                new_instance = Question.create_question(
                    question=parsed_question["question"],
                    choices=parsed_question["choices"],
                    subject=parsed_question["subject"],
                    answer=parsed_question["answer"],
                    level=parsed_question["level"],
                    hash=hashlib.sha256(
                        parsed_question["question"].encode("utf-8")
                    ).hexdigest(),
                )

                # Save to DB if unique
                if new_instance.check_uniq_save_to_db(db, collection_name="questions"):
                    questions.append(new_instance.model_dump(by_alias=True))
                    print("Generated and saved a new question.")
                    remaining_questions -= 1
                else:
                    print("Duplicate from test. Skipping save.")
        except Exception as e:
            print(f"Error generating or saving question: {e}")
            break

    print(f"Total questions prepared: {len(questions)}")

    return questions
