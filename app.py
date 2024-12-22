import secrets
from datetime import datetime

import pytz
from flask import Flask, redirect, request, flash, session
from flask_babel import gettext, format_datetime

from data.helper import (
    make_valid_url,
    convert_string_id,
    hash_password,
    compare_password,
    validate_url,
)
from data.routes import (
    show_404_error_page,
    show_info_page,
    show_modify_page,
    show_login_page,
    show_success_page,
    show_index,
)

from data.locale import init_babel

from data.db import DB, URLEntry

from config import HOST_NAME, HOST_PORT


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

init_babel(app)
_ = gettext


def add_url(url: str, password: str):
    if not url:
        flash(_("URL cannot be empty."), "error")
        return show_index()

    url = make_valid_url(url)

    if not validate_url(url):
        flash(_("Invalid URL."), "error")
        return show_index()

    with DB() as db:
        new_url_entry = URLEntry(url=url)

        if password:
            new_url_entry.password = hash_password(password)
            new_url_entry.can_be_modified = True

        db.insert(new_url_entry)

    return show_success_page(new_url_entry)


def update_url(form: dict, url_entry: URLEntry):
    new_url = form.get("url")
    if not new_url:
        flash(_("New URL cannot be empty."), "error")
    elif new_url != url_entry.url:
        url_entry.url = make_valid_url(new_url)
        with DB() as db:
            db.update_url_entry(url_entry)
        flash(_("Successfully changed URL."), "info")


def update_password(form: dict, url_entry: URLEntry):
    old_password: str = form.get("old-password", "")
    new_password: str = form.get("new-password", "")
    new_password_confirm: str = form.get("new-password-confirm", "")

    if not old_password:
        flash(_("Old password cannot be empty."), "error")
        return

    if not new_password or not new_password_confirm:
        flash(_("New password cannot be empty."), "error")
        return

    if new_password == old_password:
        flash(_("New password is the same as old one."), "error")
        return

    if new_password != new_password_confirm:
        flash(_("Passwords don't match."), "error")
        return

    if compare_password(old_password, url_entry.password):
        url_entry.password = hash_password(new_password)
        with DB() as db:
            db.update_url_entry(url_entry, False)
        flash(_("Successfully changed password."), "info")
    else:
        flash(_("Wrong password."), "error")


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        form = request.form
        return add_url(form.get("long-url", ""), form.get("password", ""))

    return show_index()


@app.route("/<short_url>")
def route_to_url(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry_by_id(url_id)
    except (TypeError, ValueError):
        return show_404_error_page(short_url)

    return redirect(url_entry.url)


@app.route("/<short_url>/info")
def short_url_info(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry_by_id(url_id)
    except (TypeError, ValueError):
        return show_404_error_page(short_url)

    return show_info_page(url_entry)


@app.route("/<short_url>/modify", methods=["GET", "POST"])
def modify_short_url(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry_by_id(url_id)
    except (TypeError, ValueError):
        return show_404_error_page(short_url)
    if url_entry.password != session.get("password"):
        return redirect("login")

    if request.method == "POST":
        form = request.form
        update_url(form, url_entry)
        update_password(form, url_entry)

    return show_modify_page(url_entry)


@app.route("/<short_url>/login", methods=["GET", "POST"])
def login(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry_by_id(url_id)
    except (TypeError, ValueError):
        return show_404_error_page(short_url)

    if request.method == "POST":
        entered_password = request.form.get("password", "")

        if compare_password(entered_password, url_entry.password):
            session["password"] = url_entry.password
            return redirect("modify")
        flash(_("Wrong password."), "error")

    return show_login_page(url_entry)


@app.template_filter("to_datetime")
def to_datetime(timestamp: float):
    date = datetime.fromtimestamp(timestamp)
    return format_datetime(date, format="medium")


@app.route("/set_timezone", methods=["POST"])
def set_timezone():
    data = request.json
    user_timezone = data.get("timeZone", "UTC")
    if user_timezone in pytz.all_timezones:
        session["timezone"] = user_timezone
    else:
        session["timezone"] = "UTC"
    return "200 OK"


if __name__ == "__main__":
    app.run(HOST_NAME, HOST_PORT, debug=True)
