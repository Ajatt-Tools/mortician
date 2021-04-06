import time
from enum import Enum

from anki.cards import Card
from anki.lang import _
from anki.notes import Note
from aqt import gui_hooks
from aqt import mw
from aqt.utils import tooltip


class Color(Enum):
    No = 0
    Red = 1
    Orange = 2
    Green = 3
    Blue = 4

    @classmethod
    def num_of(cls, color: str) -> int:
        for item in cls:
            if item.name == color:
                return item.value
        return cls.No.value


def init_config():
    _config = mw.addonManager.getConfig(__name__)

    _config['again_threshold']: int = _config.get('again_threshold', 5)
    _config['timeframe']: int = _config.get('timeframe', 24)
    _config['count_from_daystart']: bool = _config.get('count_from_daystart', False)
    _config['again_notify']: bool = _config.get('again_notify', False)
    _config['tag']: str = _config.get('tag', "potential_leech")
    _config['flag']: str = _config.get('flag', "")
    _config['disable_tooltips']: bool = _config.get('disable_tooltips', False)
    _config['no_bury']: bool = _config.get('no_bury', False)

    return _config


def notify(msg: str):
    print(msg)
    if config['disable_tooltips'] is False:
        tooltip(msg)


def milliseconds_to_hours(milliseconds) -> int:
    return int(round(milliseconds / 1000.0 / 3600.0))


def seconds_to_milliseconds(seconds) -> int:
    return int(round(seconds * 1000.0))


def hours_to_milliseconds(hours) -> int:
    return seconds_to_milliseconds(hours * 3600.0)


def current_time_milliseconds() -> int:
    return seconds_to_milliseconds(time.time())


def next_day_start_milliseconds() -> int:
    """
    Returns point in time when the next anki day starts.
    For me it's 4AM on the next day.
    """
    return seconds_to_milliseconds(mw.col.sched.dayCutoff)


def this_day_start_milliseconds() -> int:
    return next_day_start_milliseconds() - hours_to_milliseconds(24)


def threshold_time_milliseconds() -> int:
    if config['count_from_daystart'] is True:
        return this_day_start_milliseconds()
    else:
        return current_time_milliseconds() - hours_to_milliseconds(config['timeframe'])


def time_passed_hours() -> int:
    if config['count_from_daystart'] is True:
        return milliseconds_to_hours(current_time_milliseconds() - this_day_start_milliseconds())
    else:
        return config['timeframe']


def agains_in_the_timeframe(card_id: int) -> int:
    # id: epoch-milliseconds timestamp of when you did the review
    # ease: which button you pushed to score your recall. ('again' == 1)
    return mw.col.db.scalar(
        "select count() from revlog where ease = 1 and cid = ? and id >= ?",
        card_id,
        threshold_time_milliseconds()
    )


def bury_card(card_id: int) -> None:
    mw.checkpoint(_("Bury difficult card"))
    mw.col.sched.buryCards([card_id], manual=False)


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


def on_did_answer_card(_, card: Card, ease: int) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    agains = agains_in_the_timeframe(card.id)
    time_passed = time_passed_hours()

    info = f"Card {card.id} was answered again {agains} times in the past {time_passed} hours."

    if agains >= config['again_threshold']:
        if config['no_bury'] is False:
            bury_card(card.id)
            notify(f"Card buried because it was answered again {agains} times in the past {time_passed} hours.")

        decide_tag(card.note())
        decide_flag(card)
        mw.col.sched._resetLrn()
    elif config['again_notify'] is True:
        notify(info)


config = init_config()
gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
