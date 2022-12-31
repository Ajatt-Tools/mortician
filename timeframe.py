# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import time

from anki.cards import CardId
from aqt import mw

from .config import config


class TimeFrame:
    def __init__(self, hours: float = 0, seconds: float = 0, milliseconds: float = 0):
        self._milliseconds = milliseconds + self.seconds_to_milliseconds(seconds) + self.hours_to_milliseconds(hours)

    @classmethod
    def seconds_to_milliseconds(cls, seconds: float) -> float:
        return seconds * 1000

    @classmethod
    def hours_to_milliseconds(cls, hours: float) -> float:
        return cls.seconds_to_milliseconds(hours * 60 * 60)

    @classmethod
    def milliseconds_to_hours(cls, milliseconds: float) -> float:
        return milliseconds / 1000.0 / 3600.0

    def __sub__(self, other: 'TimeFrame') -> 'TimeFrame':
        return TimeFrame(milliseconds=self._milliseconds - other._milliseconds)

    def __add__(self, other: 'TimeFrame') -> 'TimeFrame':
        return TimeFrame(milliseconds=self._milliseconds + other._milliseconds)

    def milliseconds(self) -> int:
        return int(self._milliseconds)

    def hours(self) -> int:
        return int(self.milliseconds_to_hours(self._milliseconds))


def current_time() -> TimeFrame:
    return TimeFrame(seconds=time.time())


def next_day_start() -> TimeFrame:
    """
    Returns point in time when the next anki day starts.
    For me it's 4AM on the next day.
    """
    return TimeFrame(seconds=mw.col.sched.dayCutoff)


def this_day_start() -> TimeFrame:
    return next_day_start() - TimeFrame(hours=24)


def threshold_time() -> TimeFrame:
    if config['count_from_daystart'] is True:
        return this_day_start()
    else:
        return current_time() - TimeFrame(hours=config['timeframe'])


def time_passed() -> TimeFrame:
    if config['count_from_daystart'] is True:
        return current_time() - this_day_start()
    else:
        return TimeFrame(hours=config['timeframe'])


def agains_in_the_timeframe(card_id: CardId) -> int:
    # id: epoch-milliseconds timestamp of when you did the review
    # ease: which button you pushed to score your recall. ('again' == 1)
    return mw.col.db.scalar(
        "select count() from revlog where ease = 1 and cid = ? and id >= ?",
        card_id,
        threshold_time().milliseconds()
    )
