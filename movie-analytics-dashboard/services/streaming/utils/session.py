import uuid


def generate_session_id():
    return str(uuid.uuid4())


def generate_user_id():
    return uuid.uuid4().int % 1_000_000_000
