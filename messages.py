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

from typing import List

from .config import config


def get_actions() -> List[str]:
    actions = []
    if not config['no_bury']:
        actions.append('buried')
    if config['tag']:
        actions.append('tagged')
    if config['flag']:
        actions.append('flagged')
    return actions


def construct_action_report() -> str:
    actions = get_actions()
    if len(actions) < 1:
        return "Nothing has been done to card"
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


def action_msg(agains, passed):
    return f'{construct_action_report()} because it was answered "again" {agains} times in the past {passed} hours.'


def info_msg(card, agains, passed) -> str:
    return f"Card {card.id} was answered again {agains} times in the past {passed} hours."
