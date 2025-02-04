import re
from urllib.parse import urlparse
from string import ascii_letters, digits
from random import choices

from flask import request
from markupsafe import Markup
from bcrypt import hashpw, checkpw, gensalt


INVALID_CHARACTERS = '<>{}[]`^\\|%#" '
URL_MAX_SIZE = 6


def generate_short_url() -> str:
    chars = ascii_letters + digits
    return "".join(choices(chars, k=URL_MAX_SIZE))


def make_valid_url(url: str) -> str:
    if re.match(r"^http(.|):\/\/", url) is None:
        url = f"https://{url}"
    return url


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    for char in INVALID_CHARACTERS:
        if char in parsed.netloc:
            return False
    return True


def get_host_name() -> str:
    return f"http://{request.host}"


def create_complete_url(short_url: str):
    return f"{get_host_name()}/{short_url}"


def hash_password(password: str) -> bytes:
    return hashpw(password.encode("utf-8"), gensalt())


def compare_password(password: str, hashed_password: bytes) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password)


def create_url_tag(url: str, short: bool = False) -> Markup:
    if short:
        url = create_complete_url(url)
    return Markup(f'<a href="{url}">{url}</a>')
