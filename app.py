import re
import secrets


from flask import Flask, render_template, redirect, request, flash, session

from data.helper import (
    convert_integer_id,
    convert_string_id,
    hash_password,
    compare_password,
)
from data.db import DB

from config import HOST_NAME, HOST_PORT


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


def get_host_name() -> str:
    return f"http://{request.host}"


def convert_id_to_short_url(url_id: int) -> str:
    return f"{get_host_name()}/{convert_integer_id(url_id)}"


def add_url(url: str, password: str) -> str:
    if re.match("^http", url) is None:
        url = f"https://{url}"

    with DB() as db:
        if url in db.get_all_urls():
            url_id = db.get_id_by_url(url)
            short_url = convert_id_to_short_url(url_id)
            return render_template(
                "already_exists_error.html", url=url, short_url=short_url
            )
        can_be_modified = len(password) != 0
        url_id = db.insert(url, hash_password(password), can_be_modified)

    short_url = convert_id_to_short_url(url_id)

    return render_template("success.html", url=url, short_url=short_url)


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
            url_entry = db.get_url_entry(url_id)
    except (TypeError, ValueError):
        return render_template(
            "404_error.html", short_url=f"{get_host_name()}/{short_url}"
        )

    return redirect(url_entry.url)


@app.route("/<short_url>/info")
def short_url_info(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry(url_id)
    except (TypeError, ValueError):
        return render_template(
            "404_error.html", short_url=f"{get_host_name()}/{short_url}"
        )

    return render_template(
        "info.html",
        short_url=f"{get_host_name()}/{short_url}",
        url=url_entry.url,
        created_on=url_entry.created,
    )


@app.route("/<short_url>/modify", methods=["GET", "POST"])
def modify_short_url(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry(url_id)
    except (TypeError, ValueError):
        return render_template(
            "404_error.html", short_url=f"{get_host_name()}/{short_url}"
        )
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

    return render_template(
        "modify.html", can_be_modified=url_entry.can_be_modified, url=url_entry.url
    )


@app.route("/<short_url>/login", methods=["GET", "POST"])
def login(short_url: str):
    try:
        with DB() as db:
            url_id = convert_string_id(short_url)
            url_entry = db.get_url_entry(url_id)
    except (TypeError, ValueError):
        return render_template(
            "404_error.html", short_url=f"{get_host_name()}/{short_url}"
        )

    if request.method == "POST":
        entered_password = request.form["password"]

        if compare_password(entered_password, url_entry.password):
            session["password"] = url_entry.password
            return redirect("modify")
        flash("Wrong password!", "error")

    return render_template("login.html", can_be_modified=url_entry.can_be_modified)


if __name__ == "__main__":
    app.run(HOST_NAME, HOST_PORT)
