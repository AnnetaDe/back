from dotenv import load_dotenv
import os


def get_env_variable(key, default=None):
    load_dotenv()
    return os.getenv(key)
