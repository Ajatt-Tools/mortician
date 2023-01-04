# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .config import config
from .enums import Action, Color


def get_actions() -> list[str]:
    actions = []
    if config.action == Action.Bury:
        actions.append('buried')
    elif config.action == Action.Suspend:
        actions.append('suspended')
    if config['tag']:
        actions.append('tagged')
    if config.flag != Color.No:
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
