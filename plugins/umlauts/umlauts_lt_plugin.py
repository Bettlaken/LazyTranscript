import os
from typing import List

import src.util.const as c
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction

from src.util.plugin_abstract import IPlugin

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.chars = {"ae" : "ä", "oe" : "ö", "ue" : "ü", "Ae" : "Ä", "Oe" : "Ö", "Ue" : "Ü"}

    def get_toolbar_action(self, parent_window) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "umlauts", "icons", self.plugin_manager.theme, "search.png")
        action = QAction(QIcon(icon_path), "Replace umlauts", parent_window)
        action.triggered.connect(self.replace_umlauts)
        return [action]

    def replace_umlauts(self):
        text = self.plugin_manager.get_text()
        for char in self.chars:
            text = text.replace(char, self.chars[char])
        self.plugin_manager.set_text(text)

    def get_name(self) -> str:
        return "Replace Umlauts"
