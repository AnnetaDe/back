from cryptography.fernet import Fernet
import os


# key = "fTFqwkm9ZUR32Hq0FRd9gcBRuHDrbvrUpyyJ90VEuZE="
"""the only key that can decrypt the answer please dont kill it"""
key = os.getenv("KEY_ANS")
if key is None:
    raise ValueError("Environment variable KEY_ANS is not set")
f = Fernet(key)


def hide_answer(answer):
    return f.encrypt(answer.encode()).decode()


def show_answer(hidden_answer):
    return f.decrypt(hidden_answer.encode()).decode()
