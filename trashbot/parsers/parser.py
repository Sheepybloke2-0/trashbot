from __future__ import annotations

import logging
import pathlib
import yaml

import attr as attrs
from adapt.engine import IntentDeterminationEngine, DomainIntentDeterminationEngine
from adapt.intent import IntentBuilder
from dotenv import load_dotenv

from ..managers import reminder as rt, database as db, timer as tt
from ..utils import logger


@attrs.define
class Parser:
    _logger: logging.Logger = attrs.field(init=False)

    # _engine: IntentDeterminationEngine = attrs.field(init=False)
    _engine: DomainIntentDeterminationEngine = attrs.field(init=False)
    _reminder_intent: IntentBuilder = attrs.field(init=False)
    _weather_intent: IntentBuilder = attrs.field(init=False)
    _timer_intent: IntentBuilder = attrs.field(init=False)
    _reminder_keywords: list[str] = attrs.field(factory=list)
    _reminder_actions: dict[str, str] = attrs.field(factory=dict)
    _weather_keywords: list[str] = attrs.field(factory=list)
    _timer_keywords: list[str] = attrs.field(factory=list)
    _timer_actions: dict[str, str] = attrs.field(factory=dict)

    _reminder_manager: rt.ReminderManager = attrs.field(init=False)
    _timer_manager: tt.TimerManager = attrs.field(init=False)
    _dbm: db.DatabaseManager = attrs.field(init=False)

    def initialize(
        self, phrase_file_path: pathlib.Path, database_file_path: pathlib.Path
    ):
        self._logger = logger.getLogger(__name__)
        # TODO: This should be moved to the entrance at some point
        load_dotenv()
        self._logger.debug("Adding engine...")
        # self._engine = IntentDeterminationEngine()
        self._engine = DomainIntentDeterminationEngine()
        self._logger.debug("Grabbing Reminder Phrases...")
        with open(phrase_file_path, "r") as file:
            phrases = yaml.safe_load(file)
            try:
                self._reminder_keywords = phrases["adapt_phrases"]["reminders"][
                    "keywords"
                ]
                self._reminder_actions = phrases["adapt_phrases"]["reminders"][
                    "actions"
                ]
                self._timer_keywords = phrases["adapt_phrases"]["timer"]["keywords"]
                self._timer_actions = phrases["adapt_phrases"]["timer"]["actions"]
                self._weather_keywords = phrases["adapt_phrases"]["weather"]["keywords"]
            except KeyError:
                self._logger.error("Missing reminder keywords or actions!")
                raise

        self._logger.debug("Init DB connection...")
        self._dbm = db.DatabaseManager(database_file_path)

        self._engine.register_domain("ReminderDomain")
        self._engine.register_domain("TimerDomain")
        self._engine.register_domain("WeatherDomain")

        self._logger.debug("Registering Reminder Phrases...")
        for keyword in self._reminder_keywords:
            self._engine.register_entity(
                keyword, "ReminderKeywords", domain="ReminderDomain"
            )

        for action in self._reminder_actions.values():
            for keyword in action:
                self._engine.register_entity(
                    keyword, "ReminderActions", domain="ReminderDomain"
                )

        for keyword in self._timer_keywords:
            self._engine.register_entity(keyword, "TimerKeywords", domain="TimerDomain")

        for action in self._timer_actions.values():
            for keyword in action:
                self._engine.register_entity(
                    keyword, "TimerActions", domain="TimerDomain"
                )

        for keyword in self._weather_keywords:
            self._engine.register_entity(
                keyword, "WeatherKeywords", domain="WeatherDomain"
            )

        self._engine.register_regex_entity(
            "(at|for) (?P<Time>(1[0-2]|0?[1-9]):([0-5][0-9])?([AaPp][Mm]))",
            domain="ReminderDomain",
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Date>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\D?(\d{1,2}\D?))",
            domain="ReminderDomain",
        )

        self._engine.register_regex_entity(
            "(on|for) (?P<Day>((this week|next week|) (?:sun(?:day)?|mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?)))"
        )

        self._engine.register_regex_entity(
            "(for|in) (?P<TimeOffset>(tomorrow|today|two days))"
        )

        self._engine.register_regex_entity(
            "to (?P<Reminder>.*)", domain="ReminderDomain"
        )

        self._engine.register_regex_entity(
            "(in|at|for) (?P<Location>.*)", domain="WeatherDomain"
        )

        self._engine.register_regex_entity(
            "(?P<DurationHours>(([1-2][0-9]|[1-9]) hours*))", domain="TimerDomain"
        )

        self._engine.register_regex_entity(
            "for (?P<DurationMinutes>(([1-5][0-9]|[1-9]) minutes*))",
            domain="TimerDomain",
        )

        self._engine.register_regex_entity(
            "for (?P<DurationSeconds>(([1-5][0-9]|[1-9]) seconds*))",
            domain="TimerDomain",
        )

        self._logger.debug("Building intents...")
        self._reminder_intent = (
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

        self._weather_intent = (
            IntentBuilder("WeatherIntent")
            .require("WeatherKeywords")
            .optionally("Time")
            .optionally("Date")
            .optionally("Day")
            .optionally("TimeOffset")
            .require("Location")
            .build()
        )

        self._timer_intent = (
            IntentBuilder("TimerIntent")
            .require("TimerKeywords")
            .require("TimerActions")
            .optionally("DurationHours")
            .optionally("DurationMinutes")
            .optionally("DurationSeconds")
            .build()
        )

        self._logger.debug("Registering intents...")
        self._engine.register_intent_parser(
            self._reminder_intent, domain="ReminderDomain"
        )
        self._engine.register_intent_parser(
            self._weather_intent, domain="WeatherDomain"
        )
        self._engine.register_intent_parser(self._timer_intent, domain="TimerDomain")

        self._reminder_manager = rt.ReminderManager(self._reminder_actions, self._dbm)
        self._reminder_manager.init_reminders()

        self._timer_manager = tt.TimerManager(self._timer_actions)

    async def determine_intent(self, phrase: str):
        for intent in self._engine.determine_intent(phrase):
            self._logger.info("Intent: %s", intent)
            if intent.get("confidence") > 0:
                if intent["intent_type"] == "ReminderIntent":
                    self._reminder_manager.parse_and_handle_intent(intent)
                elif intent["intent_type"] == "TimerIntent":
                    await self._timer_manager.parse_and_handle_intent(intent)
                else:
                    self._logger.info("Intent: %s", intent)

    def close(self):
        if self._dbm is not None:
            self._dbm.close_db()
