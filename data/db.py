import sqlite3
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from data.helper import convert_string_id, convert_integer_id


@dataclass
class URLEntry:
    url: str = ""
    short_url: str = ""
    created: float = 0.0
    password: bytes = b""
    can_be_modified: bool = False
    last_modified: float = 0.0


DB_PATH = Path("urls.db")


class DB:
    def __init__(self) -> None:
        self.__connection = sqlite3.connect(DB_PATH)
        self.__connection.execute(
            """CREATE TABLE IF NOT EXISTS urls (
                url_id INTEGER PRIMARY KEY NOT NULL,  
                url TEXT, 
                created FLOAT, 
                password BINARY, 
                can_be_modified BOOL,
                last_modified FLOAT
            )
            """
        )
        self.__connection.commit()

        self.__connection.row_factory = sqlite3.Row

    def insert(self, new_url_entry: URLEntry):
        if not new_url_entry.url:
            raise ValueError("'new_url_entry.url' must be non empty string.")
        new_url_entry.created = datetime.now().timestamp()
        self.__connection.execute(
            "INSERT INTO urls (url, created, password, can_be_modified, last_modified) VALUES (?,?,?,?,?)",
            (
                new_url_entry.url,
                new_url_entry.created,
                new_url_entry.password,
                new_url_entry.can_be_modified,
                new_url_entry.last_modified,
            ),
        )
        self.__connection.commit()
        short_url = convert_integer_id(self.get_last_url_id())
        new_url_entry.short_url = short_url

    def _convert_fetched_data(self, fetched_data: sqlite3.Row) -> URLEntry:
        url_id, url, created, password, can_be_modified, last_modified = fetched_data
        short_url = convert_integer_id(url_id)
        url_entry = URLEntry(
            url, short_url, created, password, bool(can_be_modified), last_modified
        )
        return url_entry

    def get_url_entry_by_id(self, url_id: int) -> URLEntry:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM urls WHERE url_id=?", [url_id])
        return self._convert_fetched_data(cursor.fetchone())

    def update_url_entry(self, url_entry: URLEntry, save_update_timestamp: bool = True) -> None:
        cursor = self.__connection.cursor()
        url_id = convert_string_id(url_entry.short_url)
        if save_update_timestamp:
            url_entry.last_modified = datetime.now().timestamp()

        cursor.execute(
            "UPDATE urls SET url=?, password=?, can_be_modified=?, last_modified=? WHERE url_id=?",
            (
                url_entry.url,
                url_entry.password,
                url_entry.can_be_modified,
                url_entry.last_modified,
                url_id,
            ),
        )
        self.__connection.commit()

    def get_last_url_id(self) -> int:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT url_id FROM urls ORDER BY url_id DESC")
        res = cursor.fetchone()[0]

        if res is None:
            return 0

        return res

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.__connection.close()
