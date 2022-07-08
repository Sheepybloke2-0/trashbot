from __future__ import annotations

import datetime
import logging
import pathlib
import sqlite3

from ..utils import logger
from ..types.reminders import Reminder


class DatabaseManager:
    _logger: logging.Logger
    _db_conn: sqlite3.Connection
    _db_path: pathlib.Path

    def __init__(self, database_file_path: pathlib.Path):
        self._db_conn = None
        self._db_path = None
        self._logger = logger.getLogger(__name__)
        self.connect_db(database_file_path)
        self._logger.debug("Connected to db at %s...", self._db_path)

    def connect_db(self, database_file_path: pathlib.Path = None):
        if database_file_path is not None:
            self._db_path = database_file_path
        self._db_conn = sqlite3.connect(self._db_path)

    def close_db(self):
        self._db_conn.close()

    def check_for_table(self, name: str) -> bool:
        with self._db_conn:
            cursor = self._db_conn.execute(
                """
                SELECT count(name) FROM sqlite_master
                WHERE type='table' AND name=?
                """,
                (name,),
            )
            return cursor.fetchone()[0] == 1

    def create_reminder_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                reminder TEXT NOT NULL,
                notification_time TEXT NOT NULL
            );
        """
        self._logger.debug("Creating new table...")
        with self._db_conn:
            self._db_conn.execute(query)

    def insert_reminder(self, reminder: Reminder):
        self._logger.debug("Inserting a new reminder...")
        with self._db_conn:
            self._db_conn.execute(
                "INSERT INTO reminders (id, reminder, notification_time) VALUES (?, ?, ?);",
                (
                    str(reminder.id),
                    reminder.reminder,
                    datetime.datetime.isoformat(reminder.notification_time),
                ),
            )

    def get_reminders(self) -> list[Reminder]:
        self._logger.debug("Retrieving reminders...")
        reminders = []
        with self._db_conn:
            for row in self._db_conn.execute("SELECT * FROM reminders;"):
                self._logger.debug("row - %s", row)
                reminders.append(
                    Reminder(
                        id=int(row[0]),
                        reminder=row[1],
                        notification_time=datetime.datetime.fromisoformat(row[2]),
                    )
                )
        return reminders
