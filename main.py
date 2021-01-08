from PySide2.QtCore import QSettings

from src.windows.create_new_project import CreateNewProjectWindow
from src.windows.editor import EditorWindow
from src.windows.start import StartWindow
from PySide2.QtWidgets import QApplication
import qtmodern.styles
import qtmodern.windows
import src.util.const as c

class WindowHandler():
    """Displays the different windows and allows their interaction."""

    def __init__(self):
        """Initialize all windows and the pyside app itself."""
        self.app = QApplication()
        self.get_style()
        self.create_new_project_window = CreateNewProjectWindow(self)
        self.editor_window = EditorWindow(self)
        self.start_window = StartWindow(self)
        self.start_window.show()
        self.app.exec_()

    def get_style(self):
        """Returns the current saved style."""
        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        if self.settings.value(c.THEME, defaultValue=c.THEME_D) == c.THEME_D:
            qtmodern.styles.dark(self.app)
        else:
            qtmodern.styles.light(self.app)

    def switch_to_editor(self, project_folder_path):
        """Hides the project-window and shows the editor-window.

        Args:
          project_folder_path: Path of the project-folder

        """
        self.create_new_project_window.hide()
        self.start_window.hide()
        self.editor_window.show()
        self.editor_window.open_project(project_folder_path)

    def open_create_new_project_window(self):
        """Hides all other windows and opens the create_new_project-window."""
        self.start_window.hide()
        self.editor_window.hide()
        self.create_new_project_window.show()

if __name__ == '__main__':
    window_handler = WindowHandler()