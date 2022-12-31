# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _
from typing import Sequence

from anki.cards import CardId
from anki.collection import Collection, OpChanges
from aqt import gui_hooks
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import tooltip

from .config import config


def bury_cards(col: Collection, card_ids: Sequence[CardId]) -> OpChanges:
    pos = col.add_custom_undo_entry(_(f"Mortician: bury {len(card_ids)} cards"))
    col.sched.bury_cards(ids=card_ids, manual=True)
    return col.merge_undo_entries(pos)


def on_bury_selected(browser: Browser) -> None:
    if card_ids := browser.selected_cards():
        return CollectionOp(
            parent=browser, op=lambda col: bury_cards(col, card_ids)
        ).success(
            lambda out: tooltip(f"{len(card_ids)} cards buried.", parent=browser) if out else None
        ).run_in_background()


def setup_context_menu(browser: Browser) -> None:
    if config['show_bury_browser_action']:
        menu = browser.form.menu_Cards
        action = menu.addAction(_("Bury selected cards"))
        qconnect(action.triggered, lambda: on_bury_selected(browser))


def init():
    gui_hooks.browser_menus_did_init.append(setup_context_menu)
