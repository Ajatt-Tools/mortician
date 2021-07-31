import time
from typing import Literal

from anki.cards import Card, CardId
from anki.collection import Collection
from aqt import gui_hooks
from aqt import mw
from aqt.operations import CollectionOp, ResultWithChanges
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

    def hours(self) -> int:
        return int(self.milliseconds_to_hours(self._milliseconds))


def notify(msg: str):
    print(msg)
    if config['disable_tooltips'] is False:
        tooltip(msg, period=7000)  # TODO: move to config


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


def act_on_card(col: Collection, card: Card) -> ResultWithChanges:
    pos = col.add_custom_undo_entry("Mortician: modify difficult card")

    if config['tag'] and not (note := card.note()).has_tag(config['tag']):
        note.add_tag(config['tag'])
        col.update_note(note)

    if config['flag'] and (color_code := Color.num_of(config['flag'].capitalize())) != Color.No.value:
        card.set_user_flag(color_code)
        col.update_card(card)

    if config['no_bury'] is False:
        mw.col.sched.bury_cards([card.id, ], manual=False)

    return col.merge_undo_entries(pos)


def construct_msg():
    actions = []
    if not config['no_bury']:
        actions.append('buried')
    if config['tag']:
        actions.append('tagged')
    if config['flag']:
        actions.append('flagged')

    msg = f"Card has been {actions[0]}"
    if len(actions) == 2:
        msg += f" and {actions[1]}"
    elif len(actions) > 2:
        i = 1
        while i < len(actions) - 1:
            msg += f", {actions[i]}"
            i = i + 1
        msg += f" and {actions[-1]}"

    return msg


def on_did_answer_card(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    if config['ignore_new_cards'] is True and card.type < 2:
        return

    agains = agains_in_the_timeframe(card.id)
    passed = time_passed().hours()

    if agains >= config['again_threshold']:
        if any((config['tag'], config['flag'], not config['no_bury'])):
            msg = construct_msg() + f' because it was answered "again" {agains} times in the past {passed} hours.'
            CollectionOp(
                parent=reviewer.web, op=lambda col: act_on_card(col, card)
            ).success(
                lambda out: notify(msg) if out else None
            ).run_in_background()
    elif config['again_notify'] is True:
        info = f"Card {card.id} was answered again {agains} times in the past {passed} hours."
        notify(info)


def init():
    gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
