from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
import os
import src.util.const as c

class LicenceWidget(QWidget):
    """Widget to show the different licences."""

    def __init__(self, plugin_manager):
        super(LicenceWidget, self).__init__()
        self.plugin_manager = plugin_manager
        self.licences = QListWidget()
        self.licences.itemPressed.connect(self.on_item_pressed)

        self.label = QLabel("Click on a Item to show the Licence")

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.label)
        self.v_box.addWidget(self.licences)
        self.setLayout(self.v_box)

        self.licence_text_widget = QPlainTextEdit()
        self.licence_text_widget.setReadOnly(True)
        self.licence_text_widget.setGeometry(200, 200, 400, 400)
        self.licence_text_widget.hide()
        self.licences_paths = {}
        self.fill_licence_list()


    def fill_licence_list(self):
        """Fills the licence list with the file names"""

        for (dirpath, dirname, filenames) in os.walk(c.LICENCES_PATH):
            for file in filenames:
                self.licences_paths[file.split(".")[0]] = dirpath

        self.licences_paths.update(self.plugin_manager.get_plugin_licences())
        for key in self.licences_paths.keys():
            self.licences.addItem(QListWidgetItem(key))

    def on_item_pressed(self, item):
        """Is excecuted when an item is pressed.

        Reads the licence and opens it in another window.

        Args:
          item: The pressed item.

        """

        file = open(os.path.join(self.licences_paths.get(item.text()), item.text() + ".txt"), "r")
        text = file.read()
        file.close()

        self.licence_text_widget.setWindowTitle(item.text())
        self.licence_text_widget.setPlainText(text)
        if not self.licence_text_widget.isVisible():
            self.licence_text_widget.show()
        

class LicenceWindow(QMainWindow):
    """Window to show the different licences."""
    def __init__(self, plugin_manager):
        super(LicenceWindow, self).__init__()
        self.widget = LicenceWidget(plugin_manager)
        self.setWindowTitle("Open Source Licences")
        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))
        self.setCentralWidget(self.widget)
