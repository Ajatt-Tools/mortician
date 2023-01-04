# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.qt import *
from aqt.utils import saveGeom, restoreGeom

from .ajt_common.about_menu import menu_root_entry, tweak_window
from .ajt_common.addon_config import set_config_action
from .config import config
from .consts import *
from .enums import Color, Action


def key_to_label(key: str) -> str:
    return key.replace('_', ' ').capitalize()


def make_checkboxes() -> dict[str, QCheckBox]:
    checkboxes = {}
    for key, val in config.toggleables():
        label = key_to_label(key)
        checkboxes[key] = QCheckBox(label)
        checkboxes[key].setChecked(config[key])
    return checkboxes


def make_flag_edit_widget() -> QComboBox:
    flag_edit = QComboBox()
    flag_edit.addItems(Color.names())
    flag_edit.setCurrentText(config['flag'])
    return flag_edit


def make_action_edit_widget() -> QComboBox:
    action_edit = QComboBox()
    action_edit.addItems(Action.names())
    action_edit.setCurrentText(config['action'])
    return action_edit


def make_tag_edit_widget() -> QLineEdit:
    widget = QLineEdit(config['tag'])
    widget.currentText = widget.text
    return widget


def make_limits_widgets() -> dict[str, QSpinBox]:
    widgets = {}
    for key in INTEGER_OPTIONS.keys():
        widgets[key] = QSpinBox()
        widgets[key].setRange(1, 150)
        widgets[key].setValue(int(config[key]))

    return widgets


class SettingsDialog(QDialog):
    name = "ajt__mortician_settings_dialog"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(OPTS_WINDOW_TITLE)
        self.setMinimumSize(320, 240)
        self._checkboxes = make_checkboxes()
        self._edits: dict[str, QComboBox] = {
            'action': make_action_edit_widget(),
            'tag': make_tag_edit_widget(),
            'flag': make_flag_edit_widget(),
        }
        self._limits = make_limits_widgets()
        self._bottom_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.setLayout(self.setup_layout())
        self.connect_buttons()
        self.add_tooltips()
        tweak_window(self)
        restoreGeom(self, self.name)

    def setup_layout(self) -> QLayout:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_edits_layout())
        layout.addLayout(self.make_checkboxes_layout())
        layout.addLayout(self.make_limits_layout())
        layout.addWidget(self._bottom_box)
        return layout

    def make_checkboxes_layout(self) -> QLayout:
        layout = QVBoxLayout()
        for widget in self._checkboxes.values():
            layout.addWidget(widget)
        return layout

    def make_edits_layout(self) -> QLayout:
        layout = QFormLayout()
        for label, widget in self._edits.items():
            layout.addRow(label.capitalize(), widget)
        return layout

    def make_limits_layout(self) -> QLayout:
        layout = QGridLayout()
        lines = zip(
            (QLabel(key_to_label(key)) for key in self._limits.keys()),
            self._limits.values(),
            (QLabel(unit) for unit in INTEGER_OPTIONS.values()),
        )

        for y, line in enumerate(lines):
            for x, widget in enumerate(line):
                layout.addWidget(widget, y, x)

        return layout

    def connect_buttons(self):
        qconnect(self._bottom_box.accepted, self.accept)
        qconnect(self._bottom_box.rejected, self.reject)

    def accept(self):
        for key, widget in self._checkboxes.items():
            config[key] = widget.isChecked()
        for key, widget in self._limits.items():
            config[key] = int(widget.value())
        for key, widget in self._edits.items():
            config[key] = widget.currentText()
        config.write_config()
        return super().accept()

    def add_tooltips(self):
        self._limits['again_threshold'].setToolTip(
            "How many times a card should be failed until it gets buried.\n"
            "This setting applies to cards in the relearning queue,\n"
            "i.e. the cards that graduated at least once before."
        )
        self._limits['new_again_threshold'].setToolTip(
            "How many times a card should be failed until it gets buried.\n"
            "This setting applies to new cards."
        )
        self._limits['timeframe'].setToolTip(
            "From how many hours ago count the answers.\n"
            "Has no effect if \"count from daystart\" is enabled."
        )
        self._limits['tooltip_duration'].setToolTip(
            "How long tooltips should stay visible."
        )
        self._checkboxes['count_from_daystart'].setToolTip(
            "Ignore the \"timeframe\" setting,\n"
            "always count failed cards from the start of an Anki day.\n"
            "Usually an Anki day starts at 4AM in the morning\n"
            "but can be configured in Preferences."
        )
        self._checkboxes['again_notify'].setToolTip(
            "Show card stats after every failed review.\n"
            "This is a very annoying feature intended for debugging."
        )
        self._checkboxes['disable_tooltips'].setToolTip(
            "No matter what never show tooltips."
        )
        self._checkboxes['ignore_new_cards'].setToolTip(
            "Don't do anything to cards in the learning queue.\n"
            "If enabled, the add-on is going to act only on cards that have graduated before."
        )
        self._checkboxes['show_bury_browser_action'].setToolTip(
            "Add a button to the Anki Browser's context menu\n"
            "that lets you manually bury selected cards."
        )
        self._edits['tag'].setToolTip(
            "This tag is attached to cards when they get buried by Mortician.\n"
            "You can use the tag to find the cards in the Anki Browser later."
        )
        self._edits['flag'].setToolTip(
            "Similar to \"tag\" but adds a flag to the difficult cards.\n"
            "You can filter cards by flag in the Anki Browser."
        )
        self._edits['action'].setToolTip(
            "The main action Mortician performs on difficult cards.\n"
            "You can either bury such cards, suspend them or do nothing.\n"
            "If you choose \"No\", you can still tag or flag difficult cards\n"
            "while keeping them in the learning queue."
        )

    def done(self, *args, **kwargs) -> None:
        saveGeom(self, self.name)
        return super().done(*args, **kwargs)


def on_open_settings():
    dialog = SettingsDialog(mw)
    dialog.exec()


def setup_settings_action(parent: QWidget) -> QAction:
    action_settings = QAction(OPTS_WINDOW_TITLE + '...', parent)
    qconnect(action_settings.triggered, on_open_settings)
    return action_settings


def init():
    root_menu = menu_root_entry()
    root_menu.addAction(setup_settings_action(root_menu))
    set_config_action(on_open_settings)
