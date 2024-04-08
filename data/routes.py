from flask import render_template
from data.helper import create_complete_url

from data.db import URLEntry


def show_404_error_page(short_url: str) -> tuple[str, int]:
    return (
        render_template("404_error.html", short_url=create_complete_url(short_url)),
        404,
    )


def show_already_exists_error_page(url_entry: URLEntry) -> tuple[str, int]:
    return (
        render_template(
            "already_exists_error.html",
            url=url_entry.url,
            short_url=url_entry.short_url,
        ),
        409,
    )


def show_succes_page(new_url_entry: URLEntry) -> str:
    return render_template(
        "success.html", url=new_url_entry.url, short_url=new_url_entry.short_url
    )


def show_info_page(url_entry: URLEntry) -> str:
    return render_template(
        "info.html",
        short_url=create_complete_url(url_entry.short_url),
        url=url_entry.url,
        created_on=url_entry.created,
    )


def show_modify_page(url_entry: URLEntry) -> str:
    return render_template(
        "modify.html", can_be_modified=url_entry.can_be_modified, url=url_entry.url
    )


def show_login_page(url_entry: URLEntry) -> str:
    return render_template("login.html", can_be_modified=url_entry.can_be_modified)