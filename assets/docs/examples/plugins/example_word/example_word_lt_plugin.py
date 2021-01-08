from typing import List

from PySide2.QtCore import QThread
from PySide2.QtWidgets import QPushButton
from src.util.plugin_abstract import IPlugin
import time

NEW_WORD = "New_word"

class WordByWordThread(QThread):
    def __init__(self, parent, word, word_pos):
        super(WordByWordThread, self).__init__()
        self.parent = parent
        self.word = word
        self.word_pos = word_pos

    def run(self):
        print("start_word")
        time.sleep(60)
        new_word = self.word + "1234"
        print("end_word")
        self.parent.sig.create_button.emit(self.word, self.word_pos, {NEW_WORD: new_word})

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.sig.create_button.connect(self.done)
        self.thread = None

    def get_word_action(self, word: str, word_meta_data: List, word_pos: int):
        self.word = word
        self.word_pos = word_pos
        if self.thread is not None:
            self.thread.terminate()
        self.thread = WordByWordThread(self, word, word_pos)
        self.thread.start()

    def done(self, word, word_pos, values):
        btn = QPushButton(values[NEW_WORD])
        btn.clicked.connect(lambda: self.modify(values[NEW_WORD]))
        self.plugin_manager.add_new_word_by_word_action([btn], self.get_name(), word, word_pos)

    def modify(self, word):
        self.plugin_manager.replace_selection(word)

    def get_name(self) -> str:
        return "Long"