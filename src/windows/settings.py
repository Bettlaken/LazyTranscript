import os

from PySide2.QtCore import QSettings
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QMainWindow, QApplication, QGroupBox, QFormLayout, QVBoxLayout, \
    QLabel, QComboBox, QPushButton, QLineEdit, QCheckBox
import src.util.const as c
import re

class SettingsWidget(QWidget):
    """Widget to show and edit the settings."""

    def __init__(self):
        super(SettingsWidget, self).__init__()
        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.keyboard_settings = QSettings(c.KEYBOARD_SETTINGS_PATH, QSettings.IniFormat)

        self.value_dict_settings = {}
        self.value_dict_keyboard = {}
        self.f_reg = re.compile("F[1-9]|1[0-2]")
        self.ctrl_reg = re.compile("CTRL\+[a-xA-X0-9]")
        self.forbidden_reg = re.compile("CTRL\+[vVcCzZyY]")

        v_box = QVBoxLayout()

        theme = QGroupBox("Theme")
        theme_layout = QFormLayout()
        theme_value = QComboBox()
        theme_value.addItem(c.THEME_D)
        theme_value.addItem(c.THEME_L)
        theme_value.setCurrentText(self.settings.value(c.THEME, defaultValue=c.THEME_D))
        theme_layout.addRow(QLabel(c.THEME.capitalize()), theme_value)
        theme.setLayout(theme_layout)
        self.value_dict_settings[c.THEME] = theme_value

        keyboard = QGroupBox("Keyboard")
        keyboard_layout = QFormLayout()
        info_label = QLabel("Only F-Keys and CTRL+ Combinations are allowed.")
        info_label.setWordWrap(True)
        keyboard_layout.addRow(info_label)

        for key in self.keyboard_settings.allKeys():
            line_edit = QLineEdit()
            line_edit.setText(self.keyboard_settings.value(key))
            keyboard_layout.addRow(key, line_edit)
            self.value_dict_keyboard[key] = line_edit

        keyboard.setLayout(keyboard_layout)

        plugins = QGroupBox("Plug-ins")
        plugins_layout = QFormLayout()
        show_empty_buttons_check = QCheckBox("Show Plug-ins without Buttons in Word By Word - List")
        show_empty_buttons_check.setChecked(self.settings.value(c.SHOW_EMPTY_BUTTONS, defaultValue=True, type=bool))
        plugins_layout.addRow(show_empty_buttons_check)
        self.value_dict_settings[c.SHOW_EMPTY_BUTTONS] = show_empty_buttons_check
        plugins.setLayout(plugins_layout)

        self.note = QLabel("Settings will be applied after restart")

        save = QPushButton("Save")
        save.clicked.connect(self.save_values)

        v_box.addWidget(theme)
        v_box.addWidget(keyboard)
        v_box.addWidget(plugins)
        v_box.addWidget(self.note)
        v_box.addWidget(save)

        self.setLayout(v_box)

    def save_values(self):
        """Saves the current values."""

        saved = True
        for key in self.value_dict_settings.keys():
            widget = self.value_dict_settings.get(key)
            if isinstance(widget, QLineEdit):
                self.settings.setValue(key, widget.text().strip())
            if isinstance(widget, QComboBox):
                self.settings.setValue(key, widget.currentText().strip())
            if isinstance(widget, QCheckBox):
                self.settings.setValue(key, widget.isChecked())

        occupied = []
        self.keyboard_settings.clear()
        for key in self.value_dict_keyboard.keys():
            value = self.value_dict_keyboard.get(key).text().strip().replace(" ", "").upper()
            if len(value) == 0 or ((bool(self.f_reg.search(value)) or bool(self.ctrl_reg.search(value))) and not bool(self.forbidden_reg.search(value))):
                if value not in occupied:
                    self.keyboard_settings.setValue(key, value)
                    if len(value) != 0:
                        occupied.append(value)
                else:
                    saved = False
                    self.note.setStyleSheet("QLabel {color: red;}")
                    self.note.setText("Duplicate Values found!")
                    self.keyboard_settings.setValue(key, "")
        if saved:
            self.note.setStyleSheet("QLabel {color: green;}")
            self.note.setText("Saved!")

    def reset_note(self):
        """Resets the little now text at the bottom."""

        self.note.setStyleSheet("")
        self.note.setText("Settings will be applied after restart")


class SettingsWindow(QMainWindow):
    """Window to show and edit the settings."""

    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.widget = SettingsWidget()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))
        self.setCentralWidget(self.widget)

    def show(self) -> None:
        """Shows the window and resets the widget."""

        super(SettingsWindow, self).show()
        self.widget.reset_note()