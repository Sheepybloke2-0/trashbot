from __future__ import annotations

import asyncio
import datetime
import logging
import re

import dateparser
from numpy import mat

from ..utils import logger


class TimerManager:
    _logger: logging.Logger
    _action_keywords: dict[str, str]
    _duration_matcher: re.Pattern
    _timer: asyncio.Task
    _timer_end: datetime.timedelta

    def __init__(self, action_keywords: dict[str, str]) -> None:
        self._action_keywords = action_keywords
        self._timer = None
        self._duration_matcher = re.compile("([1-5][0-9]|[1-9])")
        self._logger = logger.getLogger(__name__)

    def _get_current_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(
            hours=datetime.datetime.now().hour,
            minutes=datetime.datetime.now().minute,
            seconds=datetime.datetime.now().second,
        )

    def _create_timedelta(
        self, hours: int = 0, minutes: int = 0, seconds: int = 0
    ) -> datetime.timedelta:
        if hours == 0 and minutes == 0 and seconds == 0:
            raise ValueError("Must have at least one value to make timedelta")
        return datetime.timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    async def _timer_runner(self):
        current_time = self._get_current_timedelta()
        while current_time <= self._timer_end:
            time_remaining = self._timer_end - current_time
            self._logger.info("Time remaining: %s", time_remaining)
            await asyncio.sleep(1.0)
            current_time = self._get_current_timedelta()

    def _start_timer(self, intent: dict[str, str]):
        self._logger.debug("Intent: %s", intent)
        hours = 0
        minutes = 0
        seconds = 0
        if intent.get("DurationHours") is not None:
            match = re.match(
                pattern=self._duration_matcher, string=intent["DurationHours"]
            )
            if match is not None:
                self._logger.debug("match %s", match)
                self._logger.debug("match %s", match.group())
                hours = int(match.group())
            else:
                self._logger.debug("No match in string %s", intent["DurationHours"])

        if intent.get("DurationMinutes") is not None:
            match = re.match(
                pattern=self._duration_matcher, string=intent["DurationMinutes"]
            )
            if match is not None:
                self._logger.debug("match %s", match)
                self._logger.debug("match %s", match.group())
                minutes = int(match.group())
            else:
                self._logger.debug("No match in string %s", intent["DurationMinutes"])

        if intent.get("DurationSeconds") is not None:
            match = re.match(
                pattern=self._duration_matcher, string=intent["DurationSeconds"]
            )
            if match is not None:
                self._logger.debug("match %s", match)
                self._logger.debug("match %s", match.group())
                seconds = int(match.group())
            else:
                self._logger.debug("No match in string %s", intent["DurationSeconds"])

        try:
            duration = self._create_timedelta(
                hours=hours, minutes=minutes, seconds=seconds
            )
        except ValueError:
            self._logger.error(
                "Looks like there was no Duration in the Intent! %s", intent
            )
            raise
        self._timer_end = self._get_current_timedelta() + duration
        self._logger.info("end %s", self._timer_end)

        self._timer = asyncio.create_task(self._timer_runner())
        self._logger.info("Added a timer!")

    def _update_timer(self, intent: dict[str, str]):
        time_str = ""
        self._logger.debug("Intent: %s", intent)
        if intent.get("DurationHours") is not None:
            time_str += intent["DurationHours"]
        if intent.get("DurationMinutes") is not None:
            time_str += " " + intent["DurationMinutes"]
        if intent.get("DurationSeconds") is not None:
            time_str += " " + intent["DurationSeconds"]

        self._timer_end = dateparser.parse(time_str, settings={"TIMEZONE": "PST"})
        self._logger.info("Updated the timer!")

    def _remove_timer(self, intent: dict[str, str]):
        self._timer.cancel()
        self._logger.info("Stopped the timer!")

    async def parse_and_handle_intent(self, intent: dict[str, str]):
        if intent["TimerActions"] in self._action_keywords["create"]:
            self._start_timer(intent)
            # TODO: Remove once we have the ui and service working
            await self._timer
        elif intent["TimerActions"] in self._action_keywords["update"]:
            self._update_timer(intent)
        elif intent["TimerActions"] in self._action_keywords["remove"]:
            self._remove_timer(intent)
        else:
            self._logger.warning("No action associated with this intent! %s", intent)
