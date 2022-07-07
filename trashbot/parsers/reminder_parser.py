from __future__ import annotations

import logging
import pathlib
import json
import yaml

import attr as attrs
from adapt.engine import IntentDeterminationEngine
from adapt.intent import IntentBuilder

from ..utils import logger


@attrs.define
class ReminderParser:
    _logger: logging.Logger = attrs.field(init=False)

    _engine: IntentDeterminationEngine = attrs.field(init=False)
    _intent: IntentBuilder = attrs.field(init=False)
    _keywords: list[str] = attrs.field(factory=list)
    _actions: list[str] = attrs.field(factory=list)

    def initialize(self, phrase_file_path: pathlib.Path):
        self._logger = logger.getLogger(__name__)
        self._logger.info("Adding engine...")
        self._engine = IntentDeterminationEngine()
        self._logger.info("Grabbing Reminder Phrases...")
        with open(phrase_file_path, "r") as file:
            phrases = yaml.safe_load(file)
            try:
                self._keywords = phrases["adapt_phrases"]["reminders"]["keywords"]
                self._actions = phrases["adapt_phrases"]["reminders"]["actions"]
            except KeyError:
                self._logger.error("Missing reminder keywords or actions!")
                raise

        self._logger.info("Registering Reminder Phrases...")
        for keyword in self._keywords:
            self._engine.register_entity(keyword, "ReminderKeywords")

        for action in self._actions:
            self._engine.register_entity(action, "ReminderActions")

        # self._engine.register_regex_entity("[at|for] (?P<Time>.*) {reminder}")
        self._engine.register_regex_entity(
            "(at|for) (?P<Time>(1[0-2]|0?[1-9]):([0-5][0-9])?([AaPp][Mm]))"
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Date>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\D?(\d{1,2}\D?))"
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Date>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\D?(\d{1,2}\D?))"
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Day>((this week|next week|) (?:sun(?:day)?|mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?)))"
        )

        self._engine.register_regex_entity("to (?P<Reminder>.*)")

        self._logger.info("Building intents...")
        self._intent = (
            IntentBuilder("ReminderIntent")
            .require("ReminderKeywords")
            .require("ReminderActions")
            .optionally("Time")
            .optionally("Date")
            .optionally("Day")
            .require("Reminder")
            .build()
        )
        self._logger.info("Registering intents...")
        self._engine.register_intent_parser(self._intent)

    def determine_intent(self, phrase: str):
        for intent in self._engine.determine_intent(phrase):
            if intent.get("confidence") > 0:
                self._logger.info("Parsed intent: %s", json.dumps(intent, indent=4))
