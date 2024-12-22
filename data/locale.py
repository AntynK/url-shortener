from flask import request, Flask, session
from flask_babel import Babel


def locale_selector() -> str:
    language = request.accept_languages.best_match(["uk", "en"])
    return language


def timezone_selector() -> str:
    return session.get("timezone", "UTC")


def init_babel(app: Flask) -> None:
    babel = Babel()
    babel.init_app(
        app,
        default_translation_directories="./locale/",
        locale_selector=locale_selector,
        timezone_selector=timezone_selector,
    )
