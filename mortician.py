from anki.cards import Card
from anki.notes import Note
from aqt import gui_hooks
from aqt import mw
from aqt.utils import tooltip
from anki.lang import _
import time

config = mw.addonManager.getConfig(__name__)

again_threshold: int = config.get('again_threshold', 5)
timeframe: int = config.get('timeframe', 24)
count_from_daystart: bool = config.get('count_from_daystart', False)
again_notify: bool = config.get('again_notify', False)
tag_on_bury: str = config.get('tag_on_bury', "potential_leech")


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
    if count_from_daystart is True:
        return this_day_start_milliseconds()
    else:
        return current_time_milliseconds() - hours_to_milliseconds(timeframe)


def time_passed_hours() -> int:
    if count_from_daystart is True:
        return milliseconds_to_hours(current_time_milliseconds() - this_day_start_milliseconds())
    else:
        return timeframe


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
    if tag_on_bury and not note.hasTag(tag_on_bury):
        note.addTag(tag_on_bury)
        note.flush()


def decide_bury(_, card: Card, ease: int) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    agains = agains_in_the_timeframe(card.id)
    time_passed = time_passed_hours()

    info = f"Card {card.id} was answered again {agains} times in the past {time_passed} hours."
    print(info)

    if agains >= again_threshold:
        bury_card(card.id)
        decide_tag(card.note())
        tooltip(f"Card buried because it was answered again {agains} times in the past {time_passed} hours.")
    elif again_notify is True:
        tooltip(info)


gui_hooks.reviewer_did_answer_card.append(decide_bury)
