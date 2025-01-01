from cryptography.fernet import Fernet


key = "fTFqwkm9ZUR32Hq0FRd9gcBRuHDrbvrUpyyJ90VEuZE="
"""the only key that can decrypt the answer please dont kill it"""
f = Fernet(key)


def hide_answer(answer):
    return f.encrypt(answer.encode()).decode()


print(hide_answer("The answer is 1234"))  # The answer is ********


def show_answer(hidden_answer):
    return f.decrypt(hidden_answer.encode()).decode()
