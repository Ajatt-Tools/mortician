from typing import Dict

from aqt import mw
from aqt.qt import *

from .color import Color
from .config import config

WINDOW_TITLE = "Mortician Options"


def get_toggleables() -> Dict[str, bool]:
    return {key: val for key, val in config.items() if type(val) == bool}


def key_to_label(key: str) -> str:
    return key.replace('_', ' ').capitalize()


def make_checkboxes() -> Dict[str, QCheckBox]:
    checkboxes = {}
    for key, val in get_toggleables().items():
        label = key_to_label(key)
        checkboxes[key] = QCheckBox(label)
        checkboxes[key].setChecked(config[key])
    return checkboxes


def make_flag_edit_widget() -> QComboBox:
    flag_edit = QComboBox()
    flag_edit.addItems(Color.colors())
    flag_edit.setCurrentIndex(Color.num_of(config['flag']))
    return flag_edit


def make_limits_widgets() -> Dict[str, QLineEdit]:
    widgets = {}
    for key in ('again_threshold', 'timeframe'):
        widgets[key] = QLineEdit()
        widgets[key].setValidator(QIntValidator())
        widgets[key].setText(str(config[key]))
    return widgets


class SettingsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(WINDOW_TITLE)
        self._checkboxes = make_checkboxes()
        self._tag_edit = QLineEdit(config['tag'])
        self._flag_edit = make_flag_edit_widget()
        self._limits = make_limits_widgets()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        self.setLayout(self.setup_layout())
        self.connect_buttons()

    def setup_layout(self) -> QLayout:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_checkboxes_layout())
        layout.addLayout(self.make_marking_layout())
        layout.addLayout(self.make_limits_layout())
        layout.addLayout(self.make_bottom_buttons())
        return layout

    def make_checkboxes_layout(self) -> QGroupBox:
        layout = QVBoxLayout()
        for widget in self._checkboxes.values():
            layout.addWidget(widget)
        return layout

    def make_marking_layout(self) -> QGridLayout:
        layout = QGridLayout()
        lines = (
            (QLabel('Tag'), self._tag_edit),
            (QLabel('Flag'), self._flag_edit)
        )

        for y, line in enumerate(lines):
            for x, widget in enumerate(line):
                layout.addWidget(widget, y, x)

        return layout

    def make_limits_layout(self) -> QGridLayout:
        layout = QGridLayout()
        lines = zip(
            (QLabel(key_to_label(key)) for key in self._limits.keys()),
            self._limits.values(),
            (QLabel(unit) for unit in ('times', 'hours')),
        )

        for y, line in enumerate(lines):
            for x, widget in enumerate(line):
                layout.addWidget(widget, y, x)

        return layout

    def make_bottom_buttons(self) -> QBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        layout.addStretch()
        return layout

    def connect_buttons(self):
        self.ok_button.clicked.connect(self.on_confirm)
        self.cancel_button.clicked.connect(self.reject)

    def on_confirm(self):
        for key, widget in self._checkboxes.items():
            config[key] = widget.isChecked()
        for key, widget in self._limits.items():
            config[key] = int(widget.text())
        config['tag'] = self._tag_edit.text()
        config['flag'] = self._flag_edit.currentText()
        mw.addonManager.writeConfig(__name__, config)
        self.accept()


def on_open_settings():
    dialog = SettingsDialog(mw)
    dialog.exec_()


def setup_settings_action():
    action_settings = QAction(WINDOW_TITLE + '...', mw)
    qconnect(action_settings.triggered, on_open_settings)
    return action_settings


mw.form.menuTools.addAction(setup_settings_action())
