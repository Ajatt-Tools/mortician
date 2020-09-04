from aqt import gui_hooks
from aqt import mw
from aqt.utils import tooltip
from anki.lang import _
import time

config = mw.addonManager.getConfig(__name__)

again_threshold: int = config['again_threshold'] if 'again_threshold' in config else 5
timeframe: int = config['timeframe'] if 'timeframe' in config else 24
count_from_daystart: bool = config['count_from_daystart'] if 'count_from_daystart' in config else False
again_notify: bool = config['again_notify'] if 'again_notify' in config else False


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


def agains_in_the_timeframe(card_id) -> int:
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


def decide_bury(reviewer, card, ease) -> None:
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
        tooltip(f"Card buried because it was answered again {agains} times in the past {time_passed} hours.")
    elif again_notify is True:
        tooltip(info)


gui_hooks.reviewer_did_answer_card.append(decide_bury)
