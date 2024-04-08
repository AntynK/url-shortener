import secrets

from flask import Flask, redirect, request, flash, session

from data.helper import (
    make_valid_url,
    convert_string_id,
    hash_password,
    compare_password,
)
from data.routes import (
    show_404_error_page,
    show_info_page,
    show_modify_page,
    show_login_page,
    show_succes_page,
    show_already_exists_error_page,
    show_index,
)

from data.db import DB, URLEntry

from config import HOST_NAME, HOST_PORT


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def add_url(url: str, password: str):
    if not url:
        flash("URL cannot be empty.", "error")
        return show_index()

    url = make_valid_url(url)

    with DB() as db:
        if url in db.get_all_urls():
            url_entry = db.get_url_entry_by_long_url(url)
            return show_already_exists_error_page(url_entry)

        new_url_entry = URLEntry(url=url, password=hash_password(password))
        new_url_entry.can_be_modified = len(password) != 0
        db.insert(new_url_entry)

    return show_succes_page(new_url_entry)


def update_url(form: dict, url_entry: URLEntry):
    new_url = form.get("url")
    if not new_url:
        flash("New URL cannot be empty.", "error")
    elif new_url != url_entry.url:
        url_entry.url = make_valid_url(new_url)
        with DB() as db:
            db.update_url_entry(url_entry)
        flash("Successfully changed URL.", "info")


def update_password(form: dict, url_entry: URLEntry):
    old_password: str = form.get("old-password", "")
    new_password: str = form.get("new-password", "")
    new_password_confirm: str = form.get("new-password-confirm", "")

    if not old_password:
        return

    if not new_password or not new_password_confirm:
        flash("New password cannot be empty.", "error")
        return

    if new_password != new_password_confirm:
        flash("Passwords don't match.", "error")
        return

    if compare_password(old_password, url_entry.password):
        url_entry.password = hash_password(new_password)
        with DB() as db:
            db.update_url_entry(url_entry)
        flash("Successfully changed password.", "info")
    else:
        flash("Wrong password.", "error")


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
        flash("Wrong password!", "error")

    return show_login_page(url_entry)


if __name__ == "__main__":
    app.run(HOST_NAME, HOST_PORT, debug=True)
