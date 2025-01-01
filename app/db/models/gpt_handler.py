import os


from gpt_handler_class import GPTHandler

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_TOKENS = 70
TEMPERATURE = 0.7
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
