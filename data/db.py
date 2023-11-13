import sqlite3
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass


@dataclass
class URLEntry:
    url: str
    url_id: int
    created: str
    password: bytes
    can_be_modified: bool


DB_PATH = Path("urls.db")


class DB:
    def __init__(self) -> None:
        self.__connection = sqlite3.connect(DB_PATH)
        self.__connection.execute(
            "CREATE TABLE IF NOT EXISTS urls (url TEXT, url_id INT, created DATETIME, password BINARY, can_be_modified BOOL)"
        )
        self.__connection.commit()

        self.__connection.row_factory = sqlite3.Row

    def insert(self, url: str, password: bytes, can_be_modified: bool) -> int:
        url_id = self.get_last_url_id() + 1
        self.__connection.execute(
            "INSERT INTO urls VALUES (?,?,?,?,?)",
            (url, url_id, datetime.now(), password, can_be_modified),
        )
        self.__connection.commit()
        return url_id

    def get_url_entry(self, url_id: int) -> URLEntry:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM urls WHERE url_id=?", [url_id])
        return URLEntry(**cursor.fetchone())

    def update_url_entry(self, url_entry: URLEntry) -> None:
        cursor = self.__connection.cursor()
        cursor.execute(
            "UPDATE urls SET url=? WHERE url_id=?",
            (url_entry.url, url_entry.url_id),
        )
        self.__connection.commit()

    def get_id_by_url(self, url: str) -> int:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT url_id FROM urls WHERE url=?", [url])
        return cursor.fetchone()[0]

    def get_all_urls(self) -> list[str]:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT url FROM urls")
        return [url[0] for url in cursor.fetchall()]

    def get_last_url_id(self) -> int:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT url_id FROM urls ORDER BY url_id DESC")
        res = cursor.fetchone()
        if res is None:
            res = [0]

        return res[0]

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.__connection.close()
