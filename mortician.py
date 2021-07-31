import time

from anki.cards import Card
from anki.lang import _
from anki.notes import Note
from aqt import gui_hooks
from aqt import mw
from aqt.utils import tooltip

from .color import Color
from .config import config


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


def on_did_answer_card(_, card: Card, ease: int) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    if config['ignore_new_cards'] is True and card.type < 2:
        return

    agains = agains_in_the_timeframe(card.id)
    time_passed = time_passed_hours()

    info = f"Card {card.id} was answered again {agains} times in the past {time_passed} hours."

    if agains >= config['again_threshold']:
        decide_tag(card.note())
        decide_flag(card)
        if config['no_bury'] is False:
            bury_card(card.id)
            notify(f"Card buried because it was answered again {agains} times in the past {time_passed} hours.")
    elif config['again_notify'] is True:
        notify(info)


gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
