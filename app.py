import re
import secrets


from flask import Flask, render_template, redirect, request, flash, session

from data.helper import (
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
)

from data.db import DB, URLEntry

from config import HOST_NAME, HOST_PORT


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def add_url(url: str, password: str):
    if re.match("^http", url) is None:
        url = f"https://{url}"

    with DB() as db:
        if url in db.get_all_urls():
            url_entry = db.get_url_entry_by_long_url(url)
            return show_already_exists_error_page(url_entry)

        new_url_entry = URLEntry(url=url, password=hash_password(password))
        new_url_entry.can_be_modified = len(password) != 0
        db.insert(new_url_entry)

    return show_succes_page(new_url_entry)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        form = request.form
        return add_url(form["long-url"], form["password"])

    return render_template("index.html")


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

        if form["url"] != url_entry.url:
            url_entry.url = form["url"]
            with DB() as db:
                db.update_url_entry(url_entry)
            flash("Successfully changed URL.", "info")
        else:
            flash("URL is the same.", "error")

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
        entered_password = request.form["password"]

        if compare_password(entered_password, url_entry.password):
            session["password"] = url_entry.password
            return redirect("modify")
        flash("Wrong password!", "error")

    return show_login_page(url_entry)


if __name__ == "__main__":
    app.run(HOST_NAME, HOST_PORT)
