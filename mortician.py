import time
from typing import Literal

from anki.cards import Card, CardId
from anki.notes import Note
from aqt import gui_hooks
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.utils import tooltip

from .color import Color
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


def notify(msg: str):
    print(msg)
    if config['disable_tooltips'] is False:
        tooltip(msg)


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


def bury_card(card_id: CardId) -> None:
    mw.checkpoint("Bury difficult card")
    mw.col.sched.bury_cards([card_id, ], manual=False)
    mw.col.sched.reset()


def decide_tag(note: Note) -> None:
    if config['tag'] and not note.hasTag(config['tag']):
        note.addTag(config['tag'])
        note.flush()


def decide_flag(card: Card) -> None:
    if config['flag']:
        color_code = Color.num_of(config['flag'].capitalize())
        if color_code != Color.No.value:
            card.setUserFlag(color_code)
            card.flush()


def on_did_answer_card(_: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    if config['ignore_new_cards'] is True and card.type < 2:
        return

    agains = agains_in_the_timeframe(card.id)
    passed = time_passed()

    info = f"Card {card.id} was answered again {agains} times in the past {passed} hours."

    if agains >= config['again_threshold']:
        decide_tag(card.note())
        decide_flag(card)
        if config['no_bury'] is False:
            bury_card(card.id)
            notify(f"Card buried because it was answered again {agains} times in the past {passed} hours.")
    elif config['again_notify'] is True:
        notify(info)


gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
