from typing import Dict

from aqt import mw
from aqt.qt import *

from .config import config
from .mortician import Color

WINDOW_TITLE = "Mortician Options"


def get_toggleables() -> Dict[str, bool]:
    return {key: val for key, val in config.items() if type(val) == bool}


def make_checkboxes() -> Dict[str, QCheckBox]:
    checkboxes = {}
    for key, val in get_toggleables().items():
        label = key.replace('_', ' ').capitalize()
        checkboxes[key] = QCheckBox(label)
        checkboxes[key].setChecked(config[key])
    return checkboxes


def make_marking_widgets() -> Dict[str, QWidget]:
    tag_widget = QLineEdit(config['tag'])
    flag_widget = QComboBox()
    flag_widget.addItems(Color.colors())
    flag_widget.setCurrentIndex(Color.num_of(config['flag']))
    flag_widget.text = flag_widget.currentText
    return {
        'tag': tag_widget,
        'flag': flag_widget,
    }


def make_numbers_widgets() -> Dict[str, QWidget]:
    widgets = {}
    for key in ('again_threshold', 'timeframe'):
        widgets[key] = QLineEdit()
        widgets[key].setValidator(QIntValidator())
        widgets[key].setText(str(config[key]))
    return widgets


class SettingsDialog(QDialog):
    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setWindowTitle(WINDOW_TITLE)
        self._checkboxes = make_checkboxes()
        self._marking = make_marking_widgets()
        self._numbers = make_numbers_widgets()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        self.setLayout(self.setup_layout())
        self.connect_buttons()

    def setup_layout(self) -> QLayout:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_checkboxes_layout())
        layout.addLayout(self.make_marking_layout())
        layout.addLayout(self.make_numbers_layout())
        layout.addLayout(self.make_bottom_buttons())
        return layout

    def make_checkboxes_layout(self) -> QGroupBox:
        layout = QVBoxLayout()
        for _, widget in self._checkboxes.items():
            layout.addWidget(widget)
        return layout

    def make_marking_layout(self) -> QGridLayout:
        layout = QGridLayout()
        grid_lines = ((QLabel(key.capitalize()), widget) for key, widget in self._marking.items())
        for y_idx, line in enumerate(grid_lines):
            for x_idx, widget in enumerate(line):
                layout.addWidget(widget, y_idx, x_idx)
        return layout

    def make_numbers_layout(self) -> QGridLayout:
        layout = QGridLayout()

        for y_idx, ((key, widget), unit) in enumerate(zip(self._numbers.items(), ('times', 'hours'))):
            layout.addWidget(QLabel(key.capitalize()), y_idx, 0)
            layout.addWidget(widget, y_idx, 1)
            layout.addWidget(QLabel(unit), y_idx, 2)

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
        for key, widget in self._marking.items():
            config[key] = widget.text()
        for key, widget in self._numbers.items():
            config[key] = int(widget.text())
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
