# -*- coding: utf-8 -*-

# Mortician add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Any modifications to this file must keep this entire header intact.

from typing import Literal

from anki.cards import Card
from anki.collection import Collection
from aqt import gui_hooks
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.utils import tooltip

from .color import Color
from .config import config
from .consts import *
from .messages import action_msg, info_msg
from .timeframe import TimeFrame, agains_in_the_timeframe, time_passed


def notify(msg: str):
    print(msg)
    if config['disable_tooltips'] is False:
        tooltip(msg, period=TimeFrame(seconds=config.get('tooltip_duration')).milliseconds())


def act_on_card(col: Collection, card: Card) -> None:
    mw.checkpoint("Mortician: modify difficult card")

    if config['tag'] and not (note := card.note()).has_tag(config['tag']):
        note.addTag(config['tag'])
        note.flush()

    if config['flag'] and (color_code := Color.num_of(config['flag'].capitalize())) != Color.No.value:
        card.setUserFlag(color_code)
        card.flush()

    if config['no_bury'] is False:
        col.sched.bury_cards([card.id, ], manual=False)
        col.sched.reset()


def threshold(card: Card) -> int:
    """Returns again threshold for the card, depending on its queue type."""
    if not card.type or card.type <= TYPE_LEARNING:
        return config.get('new_again_threshold', DEFAULT_THRESHOLD)
    else:
        return config.get('again_threshold', DEFAULT_THRESHOLD)


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
        if any((config['tag'], config['flag'], not config['no_bury'])):
            act_on_card(reviewer.mw.col, card)
            notify(action_msg(agains, passed))
    elif config['again_notify'] is True:
        notify(info_msg(card, agains, passed))


def init():
    gui_hooks.reviewer_did_answer_card.append(on_did_answer_card)
