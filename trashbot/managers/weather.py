from __future__ import annotations

import logging
import os

import dateparser

from ..utils import logger


class TimerManager:
    _logger: logging.Logger

    def __init__(self) -> None:
        self._logger = logger.getLogger(__name__)
        api_key = os.getenv("OPEN_WEATHER_API_KEY")
