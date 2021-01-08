from typing import List
from PySide2.QtCore import QThread
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QAction

from src.util.plugin_abstract import IPlugin
from language_tool_python import LanguageTool
import src.util.const as c
import os

MATCHES = "MATCHES"
CORRECTED = "CORRECTED"
TOOL = "TOOL"

class LanguageToolServerThread(QThread):

    def __init__(self):
        super(LanguageToolServerThread, self).__init__()

    def run(self):
        language_tool_path = os.path.join(c.PLUGIN_PATH, "language_tool_correction", "language_tool", "server", "languagetool-server.jar")
        n_gram_path = " --languageModel " + os.path.join(c.PLUGIN_PATH, "language_tool_correction", "language_tool", "n-gram")
        port = "8081"
        command = 'java -cp ' + language_tool_path + ' org.languagetool.server.HTTPServer --port ' + port + n_gram_path + '"'
        os.system('start cmd /k "' + command + '"')

class LanguageToolQueryThread(QThread):

    def __init__(self, tool, to_check, word_pos, parent, create_button = True):
        super(LanguageToolQueryThread, self).__init__()
        self.tool = tool
        self.to_check = to_check
        self.word_pos = word_pos
        self.parent = parent
        self.create_button = create_button

    def run(self):
        if self.tool is None:
            self.tool : LanguageTool = LanguageTool(self.parent.plugin_manager.get_language(), remote_server='http://localhost:8081')

        if self.create_button:
            matches = self.tool.check(self.to_check)
            self.parent.sig.create_button.emit(self.to_check, self.word_pos, {MATCHES: matches, TOOL: self.tool})
        else:
            corrected = self.tool.correct(self.to_check)
            self.parent.sig.execute_action.emit({CORRECTED: corrected, TOOL: self.tool})


class ReplaceButton(QPushButton):

    def __init__(self, to_replace, plugin_manager):
        super(ReplaceButton, self).__init__(to_replace)
        self.to_replace = to_replace
        self.clicked.connect(self.replace)
        self.plugin_manager = plugin_manager

    def replace(self):
        self.plugin_manager.replace_selection(self.to_replace)

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.server_thread = LanguageToolServerThread()
        self.server_thread.start()
        self.query_thread = None
        self.sig.create_button.connect(self.word_checked)
        self.sig.execute_action.connect(self.text_checked)
        self.replace_selection = False
        self.tool = None

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        self.plugin_manager.set_hint_text("Checking " + word)
        self.word_pos = word_pos

        if self.query_thread is not None:
            self.query_thread.terminate()
        self.query_thread = LanguageToolQueryThread(self.tool, word, word_pos, self)
        self.query_thread.start()


    def get_toolbar_action(self, parent) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "language_tool_correction", "icons", self.plugin_manager.theme, "spell.png")
        action = QAction(QIcon(icon_path), "Spelling", parent)
        action.triggered.connect(self.check_text)
        return [action]

    def check_text(self):
        self.plugin_manager.set_hint_text("Checking Text...")
        text = self.plugin_manager.get_selection()
        if text:
            self.replace_selection = True
        else:
            self.replace_selection = False
            text = self.plugin_manager.get_text()

        if self.query_thread is not None:
            self.query_thread.terminate()
        self.query_thread = LanguageToolQueryThread(self.tool, text, None, self, False)
        self.query_thread.start()

    def text_checked(self, args):
        corrected = args.get(CORRECTED)
        if self.replace_selection:
            self.plugin_manager.replace_selection(corrected)
        else:
            self.plugin_manager.set_text(corrected)
        self.plugin_manager.set_hint_text("Replaced to " + corrected)
        self.tool = args.get(TOOL)

    def word_checked(self, word, word_pos, args):
        if self.word_pos != word_pos:
            return

        matches = args.get(MATCHES)
        if len(matches) == 0:
            self.plugin_manager.add_new_word_by_word_action([], "No errors found", word, word_pos)
            return

        for match in matches:
            btns = []
            message = match.message
            for replacement in match.replacements:
                btn = ReplaceButton(replacement, self.plugin_manager)
                btns.append(btn)
            self.plugin_manager.add_new_word_by_word_action(btns, message, word, word_pos)

        self.tool = args.get(TOOL)


    def get_name(self) -> str:
        return "Add special Character"