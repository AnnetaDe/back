from uuid import uuid4


def unique_id(
    prefix: str = "",
) -> str:
    """
    Generate a unique ID with an optional prefix.

    :param prefix: A string to prefix the unique ID for context.
    :return: A unique string ID.
    """
    return f"{prefix}_{str(uuid4())}"
