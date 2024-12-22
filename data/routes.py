from typing import Union

from flask import render_template

from data.helper import create_url_tag
from data.db import URLEntry

response = Union[str, tuple[str, int]]


def show_403_error_page() -> response:
    return (
        render_template("403_error.html"),
        403,
    )


def show_404_error_page(short_url: str) -> response:
    return (
        render_template("404_error.html", short_url=create_url_tag(short_url, True)),
        404,
    )


def show_success_page(new_url_entry: URLEntry) -> response:
    return render_template(
        "success.html",
        url=create_url_tag(new_url_entry.url),
        short_url=create_url_tag(new_url_entry.short_url, True),
    )


def show_info_page(url_entry: URLEntry) -> response:
    return render_template(
        "info.html",
        short_url=create_url_tag(url_entry.short_url, True),
        url=create_url_tag(url_entry.url),
        created_on=url_entry.created,
        last_modified=url_entry.last_modified,
    )


def show_modify_page(url_entry: URLEntry) -> response:
    return render_template(
        "modify.html",
        can_be_modified=url_entry.can_be_modified,
        url=url_entry.url,
    )


def show_login_page(url_entry: URLEntry) -> response:
    if url_entry.can_be_modified:
        return render_template("login.html")
    return show_403_error_page()


def show_index() -> response:
    return render_template("index.html")
