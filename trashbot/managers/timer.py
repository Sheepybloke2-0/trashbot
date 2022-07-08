from __future__ import annotations

import logging

from ..utils import logger


class TimerManager:
    _logger: logging.Logger
    _action_keywords: dict[str, str]

    def __init__(self, action_keywords: dict[str, str]) -> None:
        self._action_keywords = action_keywords
        self._logger = logger.getLogger(__name__)

    def parse_and_handle_intent(self, intent: dict[str, str]):
        if intent["TimerActions"] in self._action_keywords["create"]:
            self._start_timer(intent)
        elif intent["TimerActions"] in self._action_keywords["update"]:
            self._update_timer(intent)
        elif intent["TimerActions"] in self._action_keywords["remove"]:
            self._remove_timer(intent)
        else:
            self._logger.warning("No action associated with this intent! %s", intent)
