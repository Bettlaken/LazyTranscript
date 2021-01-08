import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
from src.threads.create_new_project_thread import CreateThread
import src.util.const as c

class CreateNewProjectWidget(QWidget):
    """Widget for creating a new project."""

    def __init__(self, window_handler):
        super().__init__()
        self.file_name = None
        self.folder_path = None
        self.window_handler = window_handler

        self.v_box = QVBoxLayout()
        self.choose_file_btn = QPushButton(c.CHOOSE_FILE)
        self.choose_file_btn.clicked.connect(self.choose_file)

        self.choose_lang_combo = QComboBox()
        self.get_languages(self.choose_lang_combo)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText(c.PROJECT_NAME)

        self.choose_project_folder_btn = QPushButton(c.CHOOSE_FOLDER)
        self.choose_project_folder_btn.clicked.connect(self.choose_project_folder)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.create_new_project)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        self.v_box.addWidget(self.choose_file_btn)
        self.v_box.addWidget(self.choose_lang_combo)
        self.v_box.addWidget(self.project_name_edit)
        self.v_box.addWidget(self.choose_project_folder_btn)
        self.v_box.addWidget(self.open_btn)
        self.v_box.addWidget(self.progress_bar)

        self.setLayout(self.v_box)

    def create_new_project(self):
        """Starts the creation of the new project."""

        if self.file_name is not None and self.project_name_edit.text() != "" and self.folder_path is not None:
            self.open_btn.setEnabled(False)
            self.progress_bar.show()
            self.worker = CreateThread(self.file_name, self.folder_path, self.project_name_edit.text(), self.choose_lang_combo.currentText())
            self.worker.signal.progress.connect(self.on_new_project_progress)
            self.worker.signal.done.connect(self.on_new_project_done)
            self.worker.start()

    def on_new_project_progress(self, value):
        """Updates the progressbar with the given value from the signal.

        Args:
          value: Current %

        """

        self.progress_bar.setValue(value)

    def on_new_project_done(self, project_folder_path):
        """Is executed when the creation is done (or not).

        Args:
          project_folder_path: The project folder path if the project was successfully created, otherwise none

        """

        if project_folder_path is not None:
            self.window_handler.switch_to_editor(project_folder_path)

    def choose_file(self):
        """Opens a filepicker dialog to choose the source material."""

        filename, _ = QFileDialog.getOpenFileName(self, "Choose a File")
        if filename == "":
            return
        self.file_name = os.path.normpath(filename)
        self.choose_file_btn.setText(os.path.basename(self.file_name))

    def choose_project_folder(self):
        """Opens a folderpicker dialog to choose the folder in which the project folder will be generated."""

        folder_path = QFileDialog.getExistingDirectory(self, "Choose a Project Folder")
        if folder_path == "":
            return
        self.folder_path = os.path.normpath(folder_path)
        self.choose_project_folder_btn.setText(self.folder_path)

    def get_languages(self, combo_box):
        """Adds the available languages to the combo_box.

        Args:
          combo_box: The combo_box which will be filled with the languages

        """

        for dir in os.listdir(c.MODEL_PATH):
            combo_box.addItem(dir)

    def reset(self):
        """Resets the window."""

        self.open_btn.setEnabled(True)
        self.choose_file_btn.setText(c.CHOOSE_FILE)
        self.project_name_edit.setText("")
        self.choose_project_folder_btn.setText(c.CHOOSE_FOLDER)
        self.progress_bar.hide()
        self.file_name = None
        self.folder_path = None
        self.resize(self.minimumSize())


class CreateNewProjectWindow(QMainWindow):
    """Window for creating a new project."""

    def __init__(self, window_handler):
        super(CreateNewProjectWindow, self).__init__()
        self.setGeometry(750, 200, 300, 50)
        self.setWindowTitle("Create new Project")
        self.widget = CreateNewProjectWidget(window_handler)
        self.setCentralWidget(self.widget)
        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))

    def show(self):
        """Shows the window and resets it."""

        super(CreateNewProjectWindow, self).show()
        self.widget.reset()

