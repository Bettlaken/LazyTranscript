import os
from typing import List
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout
import src.util.const as c

from src.util.plugin_abstract import IPlugin

class TextFieldDialog(QDialog):

    PRE = "PRE"
    APPEND = "APPEND"
    REPLACE = "REPLACE"

    def __init__(self, plugin_manager):
        super(TextFieldDialog, self).__init__()
        self.plugin_manager = plugin_manager

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.edit_line = QLineEdit()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.edit_line)
        self.layout.addWidget(self.buttonBox)

        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))
        self.setWindowTitle("Word")
        self.setLayout(self.layout)

    def set_values(self, word, word_pos, action):
        self.edit_line.clear()
        self.edit_line.setFocus()
        self.word = word
        self.word_pos = word_pos
        self.action = action
        self.exec_()

    def accept(self):
        replace = False
        if self.action == self.REPLACE:
            replace = True
        if self.action == self.APPEND:
            self.word_pos = self.word_pos + 1

        self.plugin_manager.set_word_at(self.edit_line.text(), self.word_pos, replace)
        super(TextFieldDialog, self).accept()


class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.dialog = TextFieldDialog(plugin_manager)

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        pre_btn = QPushButton("Prepend Word")
        append_btn = QPushButton("Append Word")
        replace_btn = QPushButton("Replace Word")
        remove_btn = QPushButton("Remove Word")
        capitalize_btn = QPushButton("Captialze Word")
        concat_btn = QPushButton("Concat Words")

        pre_btn.clicked.connect(lambda : self.set_values(word, word_pos, self.dialog.PRE))
        append_btn.clicked.connect(lambda: self.set_values(word, word_pos, self.dialog.APPEND))
        replace_btn.clicked.connect(lambda: self.set_values(word, word_pos, self.dialog.REPLACE))
        remove_btn.clicked.connect(lambda: self.plugin_manager.set_word_at("", word_pos, True))
        capitalize_btn.clicked.connect(lambda: self.plugin_manager.set_word_at(word.capitalize(), word_pos, True))
        concat_btn.clicked.connect(lambda : self.concat(word_pos))

        self.plugin_manager.add_new_word_by_word_action([pre_btn, append_btn, capitalize_btn, replace_btn, concat_btn, remove_btn], self.get_name(), word, word_pos)

    def set_values(self, word, word_pos, action):
        self.dialog.set_values(word, word_pos, action)

    def concat(self, word_pos):
        new_word = self.plugin_manager.get_word_at(word_pos) + self.plugin_manager.get_word_at(word_pos+1)
        self.plugin_manager.set_word_at(new_word, word_pos, True)
        #self.plugin_manager.set_word_at("", word_pos+1, True)

    def get_name(self) -> str:
        return "Word"