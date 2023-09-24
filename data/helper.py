from bcrypt import hashpw, checkpw, gensalt


def convert_integer_id(url_id: int) -> str:
    return hex(url_id).replace("0x", "")


def convert_string_id(url_id: str) -> int:
    return int(url_id, base=36)


def hash_password(password: str) -> bytes:
    return hashpw(password.encode("utf-8"), gensalt())


def compare_password(password: str, hashed_password: bytes) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password)
