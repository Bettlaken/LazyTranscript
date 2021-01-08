from typing import List

from PySide2.QtWidgets import QPushButton

from src.util.plugin_abstract import IPlugin

class SpecialCharacterButton(QPushButton):

    def __init__(self, plugin_manager, special_character, new_word, word_pos, capitalize_next_word):
        super(SpecialCharacterButton, self).__init__()
        self.plugin_manager = plugin_manager
        self.new_word = new_word
        self.word_pos = word_pos
        self.capitalize_next_word = capitalize_next_word
        self.setText(special_character)
        self.clicked.connect(self.modify)

    def modify(self):
        self.plugin_manager.replace_selection(self.new_word)

        if self.capitalize_next_word:
            next_word = self.plugin_manager.get_word_at(self.word_pos + 1)
            self.plugin_manager.set_word_at(next_word.capitalize(), self.word_pos + 1, True)

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.special_characters = {".": True, ",": False, "!": True, "?": True, "(": False, ")": False}
        self.pre_chars = ["("]

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        btn_list = []
        for key in self.special_characters.keys():
            new_word = word + key
            if key in self.pre_chars:
                new_word = key + word
            btn_list.append(SpecialCharacterButton(self.plugin_manager, key, new_word, word_pos, self.special_characters.get(key)))

        self.plugin_manager.add_new_word_by_word_action(btn_list, self.get_name(), word, word_pos)

    def get_name(self) -> str:
        return "Add special Character"