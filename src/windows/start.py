import os
import src.util.const as c
from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout


class StartWidget(QWidget):
    """Widget to display the start screen."""

    def __init__(self, window_handler):
        super(StartWidget, self).__init__()
        self.window_handler = window_handler
        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.theme = self.settings.value(c.THEME, defaultValue=c.THEME_D)

        self.v_box = QVBoxLayout()
        self.h_box = QHBoxLayout()
        self.text = QLabel("What do you want to do?")
        self.text.setAlignment(Qt.AlignCenter)
        self.create_btn = QPushButton("Create new Project")
        self.create_btn.clicked.connect(window_handler.open_create_new_project_window)
        self.open_btn = QPushButton("Open Project")
        self.open_btn.clicked.connect(self.open_project)
        self.help_btn = QPushButton()
        self.help_btn.setIcon(QIcon(os.path.join(c.ICON_PATH, self.theme, "help.png")))
        self.help_btn.setMaximumWidth(20)
        self.help_btn.clicked.connect(self.open_help)
        self.help_btn.setFlat(True)

        self.emtpy = QWidget()
        self.emtpy.setMinimumWidth(20)
        self.emtpy.setMaximumWidth(20)
        self.h_box.addWidget(self.emtpy)
        self.h_box.addWidget(self.text)
        self.h_box.addWidget(self.help_btn)

        self.v_box.addLayout(self.h_box)
        self.v_box.addWidget(self.create_btn)
        self.v_box.addWidget(self.open_btn)
        self.setLayout(self.v_box)

    def open_project(self):
        """Opens a folder dialog to open an existing project."""

        folder_path = QFileDialog.getExistingDirectory(self, "Choose a Project Folder")
        if folder_path == "":
            return
        self.folder_path = os.path.normpath(folder_path)
        self.window_handler.switch_to_editor(folder_path)

    def open_help(self):
        """Opens the manual with the systems standard pdf reader."""

        guide_path = os.path.join(c.ASSETS_PATH, "docs", "manual.pdf")
        os.system(guide_path)


class StartWindow(QMainWindow):
    """Window to display the start screen."""
    def __init__(self, window_handler):
        super(StartWindow, self).__init__()
        self.setGeometry(750, 200, 300, 50)
        self.setWindowTitle("LazyTranscript")
        self.widget = StartWidget(window_handler)
        self.setCentralWidget(self.widget)
        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))