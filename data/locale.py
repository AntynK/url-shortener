from flask import request, Flask
from flask_babel import Babel


def locale_selector() -> str:
    language = request.accept_languages.best_match(["uk", "en"])
    return language


def init_babel(app: Flask) -> None:
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "./locale"
    app.config["BABEL_DEFAULT_LOCALE"] = "en"

    babel = Babel()
    babel.init_app(app, locale_selector=locale_selector)
