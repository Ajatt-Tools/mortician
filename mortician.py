# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Literal, cast

from anki.cards import Card
from anki.collection import Collection
from aqt import gui_hooks
from aqt.operations import CollectionOp, ResultWithChanges
from aqt.qt import QWidget
from aqt.reviewer import Reviewer
from aqt.utils import tooltip

from .config import config
from .consts import *
from .enums import Action, Color
from .messages import action_msg, info_msg
from .timeframe import TimeFrame, agains_in_the_timeframe, time_passed


def notify(msg: str):
    print(msg)
    if config['disable_tooltips'] is False:
        tooltip(msg, period=TimeFrame(seconds=config['tooltip_duration']).milliseconds())


def sched_reset(col: Collection) -> None:
    # V2 and V1 have _resetLrn(). On V3 it's not needed.
    if func := getattr(col.sched, '_resetLrn', None):
        func()


def act_on_card(col: Collection, card: Card) -> ResultWithChanges:
    pos = col.add_custom_undo_entry("Mortician: modify difficult card")

    if config['tag'] and not (note := card.note()).has_tag(config['tag']):
        note.add_tag(config['tag'])
        col.update_note(note)

    if Color.No != config.flag != Color(card.user_flag()):
        col.set_user_flag_for_cards(config.flag.value, cids=[card.id, ])

    if config.action == Action.Bury:
        col.sched.bury_cards(ids=[card.id, ], manual=False)
        sched_reset(col)
    elif config.action == Action.Suspend:
        col.sched.suspend_cards(ids=[card.id, ])
        sched_reset(col)

    return col.merge_undo_entries(pos)


def threshold(card: Card) -> int:
    """Returns again threshold for the card, depending on its queue type."""
    if not card.type or card.type <= TYPE_LEARNING:
        return config['new_again_threshold']
    else:
        return config['again_threshold']


def on_did_answer_card(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]) -> None:
    """Bury card if it was answered 'again' too many times within the specified time."""

    # only care about failed cards
    if ease != 1:
        return

    if config['ignore_new_cards'] is True and card.type <= TYPE_LEARNING:
        return

    agains = agains_in_the_timeframe(card.id)
    passed = time_passed().hours()

    if agains >= threshold(card):
        if config['tag'] or config['flag'] or config.action != Action.No:
            CollectionOp(
                parent=cast(QWidget, reviewer.web), op=lambda col: act_on_card(col, card)
            ).success(
                lambda out: notify(action_msg(agains, passed)) if out else None
            ).run_in_background()
    elif config['again_notify'] is True:
        notify(info_msg(card, agains, passed))


def init():
    gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
