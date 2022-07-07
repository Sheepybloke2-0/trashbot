from __future__ import annotations

import datetime
import logging
import pathlib
import sqlite3
import uuid

import attr as attrs
import dateparser
from regex import R

from ..utils import logger


@attrs.define
class Reminder:
    id: int
    notification_time: datetime.datetime
    reminder: str


class ReminderManager:
    _logger: logging.Logger
    _reminders: dict[int, Reminder]
    _action_keywords: dict[str, str]
    _db_conn: sqlite3.Connection
    _db_cursor: sqlite3.Cursor

    def __init__(self, action_keywords: dict[str, str]) -> None:
        self._reminders = {}
        self._action_keywords = action_keywords
        self._db_conn = None
        self._db_cursor = None
        self._db_path = None
        self._logger = logger.getLogger(__name__)

    def connect_db(self, database_file_path: pathlib.Path = None):
        if database_file_path is not None:
            self._db_path = database_file_path
        self._db_conn = sqlite3.connect(self._db_path)
        self._db_cursor = self._db_conn.cursor()

    def close_db(self):
        self._db_conn.commit()
        self._db_conn.close()

    def insert_reminder(self, reminder: Reminder):
        self.connect_db()
        self._db_cursor.execute(
            "INSERT INTO reminders (id, reminder, notification_time) VALUES (?, ?, ?);",
            (
                str(reminder.id),
                reminder.reminder,
                datetime.datetime.isoformat(reminder.notification_time),
            ),
        )
        self.close_db()

    def init_reminders(self, database_file_path: pathlib.Path):
        self.connect_db(database_file_path=database_file_path)
        self._logger.info("Retrieving reminders...")
        for row in self._db_cursor.execute("SELECT * FROM reminders;"):
            self._logger.info("Reminder: %s", row)
            self._reminders[row[0]] = Reminder(
                id=row[0],
                reminder=row[1],
                notification_time=datetime.datetime.fromisoformat(row[2]),
            )
        self.close_db()

    def _create_reminder(self, intent: dict[str, str]):
        date_str = ""
        self._logger.debug("Intent: %s", intent)
        if intent.get("Date") is not None:
            # TODO: Can we have date and day in the same object?
            date_str += intent["Date"]
        elif intent.get("Day") is not None:
            date_str += intent["Day"]
        elif intent.get("TimeOffset") is not None:
            date_str += intent["TimeOffset"]

        if intent.get("Time") is not None:
            date_str += " " + intent["Time"]

        parsed_time = dateparser.parse(date_str)
        if datetime.datetime.now().date() >= parsed_time.date():
            parsed_time = parsed_time.replace(year=parsed_time.year + 1)
        self._logger.debug("Parsed time: %s", parsed_time)
        new_reminder = Reminder(
            id=uuid.uuid4().int,
            reminder=intent["Reminder"],
            notification_time=parsed_time,
        )

        self.insert_reminder(new_reminder)
        self._reminders[new_reminder.id] = new_reminder
        self._logger.info(
            "Added a reminder to %s at %s",
            self._reminders[new_reminder.id].reminder,
            self._reminders[new_reminder.id].notification_time,
        )

    def _delete_reminder(self, intent: dict[str, str]):
        self._logger.critical("LOL MAYBE SOMEDAY! %s", intent)

    def _update_reminder(self, intent: dict[str, str]):
        self._logger.critical("LOL UPDATEMECAPPIN! %s", intent)

    def parse_and_handle_intent(self, intent: dict[str, str]):
        if intent["ReminderActions"] in self._action_keywords["create"]:
            self._create_reminder(intent)
        elif intent["ReminderActions"] in self._action_keywords["update"]:
            self._update_reminder(intent)
        elif intent["ReminderActions"] in self._action_keywords["remove"]:
            self._remove_reminder(intent)
        else:
            self._logger.warning("No action associated with this intent! %s", intent)
