import os

from PySide2.QtCore import QSettings
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
import src.util.const as c


class TextModuleWidget(QWidget):
    """Widget to display and define the text modules."""

    def __init__(self, parent):
        super(TextModuleWidget, self).__init__()
        self.parent = parent

        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.table = QTableWidget()
        self.init_table()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.on_save)

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.table)
        self.v_box.addWidget(self.save_btn)

        self.setLayout(self.v_box)

    def init_table(self):
        """Initialize the table with the currently saved text modules."""

        text_modules = self.settings.value(c.TEXT_MODULES, defaultValue={})
        self.table.setRowCount(len(text_modules) + 1)
        self.table.setColumnCount(2)

        i = 0
        for key in text_modules.keys():
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(text_modules.get(key)))
            i += 1

        self.table.setItem(i, 0, QTableWidgetItem(""))
        self.table.setItem(i, 1, QTableWidgetItem(""))

        self.table.setHorizontalHeaderLabels(["Short", "Word"])
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.table.itemChanged.connect(self.on_item_change)

    def on_save(self):
        """Saves the text_modules."""

        text_modules = {}
        for row_num in range(0, self.table.rowCount() - 1):
            item_0 = self.table.item(row_num, 0)
            item_1 = self.table.item(row_num, 1)
            if item_0.text().strip() != "" and item_1.text().strip() != "":
                text_modules[item_0.text().strip()] = item_1.text().strip()

        self.settings.setValue(c.TEXT_MODULES, text_modules)
        # add here the value from the checkbox so it does not need to be safed in settings for first start
        self.parent.on_text_modules_change()

    def on_item_change(self):
        """Adds and remove rows from the table so alaways one empty is visible."""

        changed = self.table.selectedItems()[0]

        if changed.row() + 1 == self.table.rowCount() and changed.text() != "":
            self.table.setRowCount(self.table.rowCount() + 1)
            self.table.setItem(self.table.rowCount() + 1, 0, QTableWidgetItem(""))
            self.table.setItem(self.table.rowCount() + 1, 1, QTableWidgetItem(""))

        to_remove = []
        for row_num in range(0, self.table.rowCount() - 1):
            item_0 = self.table.item(row_num, 0)
            item_1 = self.table.item(row_num, 1)
            if item_0.text() == "" and item_1.text() == "":
                to_remove.append(row_num)

        for i in to_remove:
            self.table.removeRow(i)

        self.table.update()
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

class TextModuleWindow(QMainWindow):
    """Window to display and define the text modules."""

    def __init__(self, parent):
        super(TextModuleWindow, self).__init__()
        self.setWindowTitle("Text modules")
        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))
        self.widget = TextModuleWidget(parent)
        self.setCentralWidget(self.widget)
