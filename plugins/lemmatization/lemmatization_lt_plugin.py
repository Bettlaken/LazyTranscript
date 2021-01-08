import os
from typing import List

from PySide2.QtCore import QThread
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction
from src.util.plugin_abstract import IPlugin
from HanTa import HanoverTagger
import src.util.const as c

NEW_TEXT = "NEW_TEXT"

class LemmThread(QThread):

    def __init__(self, parent, to_check, tagger):
        super(LemmThread, self).__init__()
        self.tagger = tagger
        self.to_check = to_check
        self.parent = parent

    def run(self):
        self.to_check = self.to_check.split()
        tags = self.tagger.tag_sent(self.to_check)
        new_text = []
        for org, found, lem in tags:
            if lem in ['NN', 'NNS', 'NNP', 'NNPS']:
                new_text.append(org.capitalize())
            else:
                new_text.append(org)

        self.parent.sig.execute_action.emit({NEW_TEXT: " ".join(new_text)})

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.tagger = HanoverTagger.HanoverTagger('morphmodel_ger.pgz')
        self.thread = None
        self.sig.execute_action.connect(self.replace_text)

    def get_toolbar_action(self, parent_window) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "lemmatization", "icons", self.plugin_manager.theme, "lem.png")
        action = QAction(QIcon(icon_path), "Lemmatization", parent_window)
        action.triggered.connect(self.capitalize_nouns)
        return [action]

    def capitalize_nouns(self):
        if "de" in self.plugin_manager.get_language():
            if self.thread is not None:
                self.thread.terminate()
            self.thread = LemmThread(self, self.plugin_manager.get_text(), self.tagger)
            self.thread.start()

    def replace_text(self, dict):
        new_text = dict[NEW_TEXT]
        self.plugin_manager.set_text_with_line_breaks(new_text)

    def get_name(self) -> str:
        return "Capitalize Nouns"
