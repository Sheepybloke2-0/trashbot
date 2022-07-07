from __future__ import annotations

import datetime
import logging
import uuid

import dateparser

from ..utils import logger
from .database import DatabaseManager
from ..types.reminders import Reminder


class ReminderManager:
    _logger: logging.Logger
    _reminders: dict[int, Reminder]
    _action_keywords: dict[str, str]
    _dbm: DatabaseManager

    def __init__(self, action_keywords: dict[str, str]) -> None:
        self._reminders = {}
        self._dbm = None
        self._action_keywords = action_keywords
        self._logger = logger.getLogger(__name__)

    def init_reminders(self, dbm: DatabaseManager):
        self._dbm = dbm
        reminders = self._dbm.get_reminders()
        for reminder in reminders:
            self._reminders[reminder.id] = reminder

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

        parsed_time = dateparser.parse(date_str, settings={"TIMEZONE": "PST"})
        if datetime.datetime.now().date() > parsed_time.date():
            parsed_time = parsed_time.replace(year=parsed_time.year + 1)
        self._logger.debug("Parsed time: %s", parsed_time)
        new_reminder = Reminder(
            id=uuid.uuid4().int,
            reminder=intent["Reminder"],
            notification_time=parsed_time,
        )

        self._dbm.insert_reminder(new_reminder)
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
