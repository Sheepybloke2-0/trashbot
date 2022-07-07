from __future__ import annotations

import logging
import pathlib
import yaml

import attr as attrs
from adapt.engine import IntentDeterminationEngine
from adapt.intent import IntentBuilder

from ..managers import reminder as rt, database as db
from ..utils import logger


@attrs.define
class ReminderParser:
    _logger: logging.Logger = attrs.field(init=False)

    _engine: IntentDeterminationEngine = attrs.field(init=False)
    _intent: IntentBuilder = attrs.field(init=False)
    _keywords: list[str] = attrs.field(factory=list)
    _actions: dict[str, str] = attrs.field(factory=dict)

    _manager: rt.ReminderManager = attrs.field(init=False)
    _dbm: db.DatabaseManager = attrs.field(init=False)

    def initialize(
        self, phrase_file_path: pathlib.Path, database_file_path: pathlib.Path
    ):
        self._logger = logger.getLogger(__name__)
        self._logger.debug("Adding engine...")
        self._engine = IntentDeterminationEngine()
        self._logger.debug("Grabbing Reminder Phrases...")
        with open(phrase_file_path, "r") as file:
            phrases = yaml.safe_load(file)
            try:
                self._keywords = phrases["adapt_phrases"]["reminders"]["keywords"]
                self._actions = phrases["adapt_phrases"]["reminders"]["actions"]
            except KeyError:
                self._logger.error("Missing reminder keywords or actions!")
                raise

        self._logger.debug("Init DB connection...")
        self._dbm = db.DatabaseManager(database_file_path)

        self._logger.debug("Registering Reminder Phrases...")
        for keyword in self._keywords:
            self._engine.register_entity(keyword, "ReminderKeywords")

        for action in self._actions.values():
            for keyword in action:
                self._engine.register_entity(keyword, "ReminderActions")

        # self._engine.register_regex_entity("[at|for] (?P<Time>.*) {reminder}")
        self._engine.register_regex_entity(
            "(at|for) (?P<Time>(1[0-2]|0?[1-9]):([0-5][0-9])?([AaPp][Mm]))"
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Date>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\D?(\d{1,2}\D?))"
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Day>((this week|next week|) (?:sun(?:day)?|mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?)))"
        )

        self._engine.register_regex_entity(
            "(for|in) (?P<TimeOffset>(tomorrow|today|two days))"
        )

        self._engine.register_regex_entity("to (?P<Reminder>.*)")

        self._logger.debug("Building intents...")
        self._intent = (
            IntentBuilder("ReminderIntent")
            .require("ReminderKeywords")
            .require("ReminderActions")
            .optionally("Time")
            .optionally("Date")
            .optionally("Day")
            .optionally("TimeOffset")
            .require("Reminder")
            .build()
        )
        self._logger.debug("Registering intents...")
        self._engine.register_intent_parser(self._intent)

        self._manager = rt.ReminderManager(self._actions)
        self._manager.init_reminders(dbm=self._dbm)

    def determine_intent(self, phrase: str):
        for intent in self._engine.determine_intent(phrase):
            if intent.get("confidence") > 0:
                if intent["intent_type"] == "ReminderIntent":
                    self._manager.parse_and_handle_intent(intent)

    def close(self):
        self._dbm.close_db()
