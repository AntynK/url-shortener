import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass

from data.helper import generate_short_url


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
                url_id CHAR(6) PRIMARY KEY NOT NULL,  
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

    def insert(self, url_entry: URLEntry) -> None:
        """Insert a URL entry into the database.
        `IMPORTANT`: This function also updates the `short_url` and `created` attributes of `url_entry`.

        Args:
            url_entry (URLEntry): URL entry to be inserted.

        Raises:
            ValueError: if `url_entry.url` is empty or None.
        """

        if not url_entry.url:
            raise ValueError("'url_entry.url' must be non empty string.")
        url_entry.created = datetime.now(timezone.utc).timestamp()
        url_entry.short_url = generate_short_url()
        self.__connection.execute(
            "INSERT INTO urls (url_id, url, created, password, can_be_modified, last_modified) VALUES (?,?,?,?,?,?)",
            (
                url_entry.short_url,
                url_entry.url,
                url_entry.created,
                url_entry.password,
                url_entry.can_be_modified,
                url_entry.last_modified,
            ),
        )
        self.__connection.commit()

    def _generate_id(self) -> str:
        url_id = ""
        while 1:
            url_id = generate_short_url()
            cursor = self.__connection.cursor()
            cursor.execute("SELECT 1 FROM urls WHERE url_id=?", [url_id])
            print(cursor.fetchone())

        return url_id

    def _convert_fetched_data(self, fetched_data: sqlite3.Row) -> URLEntry:
        url_id, url, created, password, can_be_modified, last_modified = fetched_data
        url_entry = URLEntry(
            url, url_id, created, password, bool(can_be_modified), last_modified
        )
        return url_entry

    def get_url_entry_by_id(self, url_id: str) -> URLEntry:
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM urls WHERE url_id=?", [url_id])
        return self._convert_fetched_data(cursor.fetchone())

    def update_url_entry(
        self, url_entry: URLEntry, save_update_timestamp: bool = True
    ) -> None:
        """Update existing URL entry in the database.
        `IMPORTANT` this function also changes `last_modified` attribute of `url_entry` if `save_update_timestamp` is True.

        Args:
            url_entry (URLEntry): _description_
            save_update_timestamp (bool, optional): _description_. Defaults to True.
        """
        cursor = self.__connection.cursor()
        if save_update_timestamp:
            url_entry.last_modified = datetime.now().timestamp()

        cursor.execute(
            "UPDATE urls SET url=?, password=?, can_be_modified=?, last_modified=? WHERE url_id=?",
            (
                url_entry.url,
                url_entry.password,
                url_entry.can_be_modified,
                url_entry.last_modified,
                url_entry.short_url,
            ),
        )
        self.__connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.__connection.close()
