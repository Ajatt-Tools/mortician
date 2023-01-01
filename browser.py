# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _, ngettext
from typing import Sequence

from anki.cards import CardId, Card
from anki.collection import Collection, OpChanges
from aqt import gui_hooks
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *
from aqt.utils import tooltip

from .config import config

ATTR_NAME = 'ajt__toggle_bury_action'


def undo_name(action: str, num_items: int) -> str:
    return _(f"Mortician: {action} {num_items} {ngettext('card', 'cards', num_items)}")


def bury_cards(col: Collection, card_ids: Sequence[CardId]) -> OpChanges:
    pos = col.add_custom_undo_entry(undo_name('bury', len(card_ids)))
    col.sched.bury_cards(ids=card_ids, manual=True)
    return col.merge_undo_entries(pos)


def unbury_cards(col: Collection, card_ids: Sequence[CardId]) -> OpChanges:
    pos = col.add_custom_undo_entry(undo_name('unbury', len(card_ids)))
    col.sched.unbury_cards(ids=card_ids)
    return col.merge_undo_entries(pos)


def toggle_bury_of_selected_notes(browser: Browser, checked: bool) -> None:
    if card_ids := browser.selected_cards():
        return CollectionOp(
            # Checked state flips when the user clicks on the action,
            # thus if checked is True then cards should be buried.
            parent=browser, op=lambda col: (bury_cards(col, card_ids) if checked else unbury_cards(col, card_ids))
        ).success(
            lambda out: tooltip(f"{len(card_ids)} cards buried.", parent=browser) if out else None
        ).run_in_background()


def setup_context_menu(browser: Browser) -> None:
    if config['show_bury_browser_action']:
        menu = browser.form.menu_Cards
        action = menu.addAction(_("Toggle Bury selected cards"))
        qconnect(action.triggered, lambda checked: toggle_bury_of_selected_notes(browser, checked))
        action.setCheckable(True)
        setattr(browser, ATTR_NAME, action)


def is_buried(card: Card) -> bool:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure#cards
    return card.queue in (-3, -2)


def update_toggle_bury_action(browser: Browser) -> None:
    if hasattr(browser, ATTR_NAME):
        is_current_buried = bool(
            browser.current_card and is_buried(browser.current_card)
        )
        getattr(browser, ATTR_NAME).setChecked(is_current_buried)


def init():
    gui_hooks.browser_menus_did_init.append(setup_context_menu)
    gui_hooks.browser_did_change_row.append(update_toggle_bury_action)
