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

        self._logger.info("Building intents...")
        self._intent = (
            IntentBuilder("ReminderIntent").require("ReminderKeywords").build()
        )
        self._logger.info("Registering intents...")
        self._engine.register_intent_parser(self._intent)

    def determine_intent(self, phrase: str):
        for intent in self._engine.determine_intent(phrase):
            self._logger.info("Intent: %s", intent)
            if intent.get("confidence") > 0:
                self._logger.info("Parsed intent: %s", json.dumps(intent, indent=4))
