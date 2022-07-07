from __future__ import annotations

import datetime

import attr as attrs


@attrs.define
class Reminder:
    id: int
    notification_time: datetime.datetime
    reminder: str
