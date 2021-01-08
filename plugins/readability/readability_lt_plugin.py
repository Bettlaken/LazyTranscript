import os
import re
from typing import List
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import *
from src.util.plugin_abstract import IPlugin
import src.util.const as c
import pyphen

class ReadabilityWidget(QWidget):

    def __init__(self, plugin_manager):
        super(ReadabilityWidget, self).__init__()
        self.plugin_manager =  plugin_manager

        icon_path = os.path.join(c.ICON_PATH, "neutral", "quote.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Readability")

        self.v_box = QVBoxLayout()

        self.header = QLabel()
        self.header.setAlignment(Qt.AlignCenter)
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.init_table()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_score)
        self.info = QLabel("Source: https://de.wikipedia.org/wiki/Lesbarkeitsindex#Flesch_Reading_Ease \nLicence: https://creativecommons.org/licenses/by-sa/3.0/legalcode")
        self.info.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.v_box.addWidget(self.header)
        self.v_box.addWidget(self.table)
        self.v_box.addWidget(self.refresh_btn)
        self.v_box.addWidget(self.info)

        self.setLayout(self.v_box)
        self.setFixedSize(404, 260)

    def show(self):
        super(ReadabilityWidget, self).show()
        self.refresh_score()

    def refresh_score(self):
        self.reset_color()
        text = self.plugin_manager.get_text()

        if text.count(".") == 0:
            return

        only_words = re.sub(r"[^a-zA-Z0-9 äöü]","", text)

        lang = self.plugin_manager.get_language()
        dict = pyphen.Pyphen(lang=lang.replace("-", "_"))

        # german values
        v1 = 180
        v2 = 1
        v3 = 58.5

        if lang == "en-US":
            v1 = 206.835
            v2 = 1.015
            v3 = 84.6

        fre = v1 - (v2 * self.get_sentence_length(text)) - (v3 * self.get_avg_syllables(only_words, dict))
        self.header.setText("Flesch-Reading-Ease: " + str(round(fre, 2)))
        row = 0

        if fre<30:
            row = 0
        elif fre<50:
            row = 1
        elif fre<60:
            row = 2
        elif fre<70:
            row = 3
        elif fre<80:
            row = 4
        elif fre < 90:
            row = 5
        else:
            row = 6

        for i in range(0, 3):
            self.table.item(row, i).setBackground(Qt.darkGreen)

    def reset_color(self):
        for i in range(0, 7):
            for j in range(0, 3):
                self.table.item(i, j).setBackground(Qt.transparent)

    def get_sentence_length(self, text):
        word_count = len(text.split())
        punc_count = text.count(".")
        return word_count/punc_count

    def get_avg_syllables(self, words, dict):
        words = words.split()
        syllables_count = 0

        for word in words:
            syllables_count += len(dict.inserted(word).split("-"))

        return syllables_count / len(words)

    def init_table(self):
        self.table.setRowCount(7)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Flesch-Reading-Ease-Score", "Readability", "Understandable for"])
        font = self.table.font()
        font.setBold(True)
        self.table.horizontalHeader().setFont(font)

        self.table.setItem(0, 0, QTableWidgetItem("0-30"))
        self.table.setItem(1, 0,  QTableWidgetItem("30-50"))
        self.table.setItem(2, 0, QTableWidgetItem("50-60"))
        self.table.setItem(3, 0, QTableWidgetItem("60-70"))
        self.table.setItem(4, 0, QTableWidgetItem("70-80"))
        self.table.setItem(5, 0, QTableWidgetItem("80-90"))
        self.table.setItem(6, 0, QTableWidgetItem("90-100"))

        self.table.setItem(0, 1, QTableWidgetItem("Very Hard"))
        self.table.setItem(1, 1, QTableWidgetItem("Hard"))
        self.table.setItem(2, 1, QTableWidgetItem("Moderate"))
        self.table.setItem(3, 1, QTableWidgetItem("Medium"))
        self.table.setItem(4, 1, QTableWidgetItem("Medium easy"))
        self.table.setItem(5, 1, QTableWidgetItem("Easy"))
        self.table.setItem(6, 1, QTableWidgetItem("Very Easy"))


        self.table.setItem(0, 2, QTableWidgetItem("Academics"))
        self.table.setItem(1, 2, QTableWidgetItem(""))
        self.table.setItem(2, 2, QTableWidgetItem(""))
        self.table.setItem(3, 2, QTableWidgetItem("13-15 year old students"))
        self.table.setItem(4, 2, QTableWidgetItem(""))
        self.table.setItem(5, 2, QTableWidgetItem(""))
        self.table.setItem(6, 2, QTableWidgetItem("11 year old students"))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)


class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.widget = ReadabilityWidget(plugin_manager)

    def get_toolbar_action(self, parent_window) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "readability", "icons", self.plugin_manager.theme, "read.png")
        action = QAction(QIcon(icon_path), "Readability", parent_window)
        action.triggered.connect(self.show_widget)
        return [action]

    def show_widget(self):
        if self.widget.isVisible():
            self.widget.hide()
        else:
            self.widget.show()

    def get_name(self) -> str:
        return "Readability"

if __name__ == '__main__':
    app = QApplication()
    window = ReadabilityWidget(None)
    window.show()
    app.exec_()