from typing import List

from PySide2.QtWidgets import QPushButton
from src.util.plugin_abstract import IPlugin
from plugins.word_to_number.word_to_number import WordToNumberConverter
from plugins.word_to_number.w2n import word_to_num

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.conv = WordToNumberConverter()

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        if "de" in self.plugin_manager.get_language().lower():
            number = self.conv.map_word_to_number(word.lower())
        elif "en" in self.plugin_manager.get_language().lower():
            try:
                number = word_to_num(word)
            except:
                number = word
        else:
            self.plugin_manager.set_hint_text("not supported language")
            return

        if number == word.lower():
            #self.plugin_manager.add_new_word_by_word_action([], self.get_name(), word, word_pos)
            return

        btn = QPushButton(str(number))
        btn.clicked.connect(lambda : self.plugin_manager.set_word_at(number, word_pos, True))

        self.plugin_manager.add_new_word_by_word_action([btn], self.get_name(), word, word_pos)

    def get_name(self) -> str:
        return "Numbers"