import os
from typing import List

from PySide2.QtCore import QThread
import src.util.const as c
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction
from src.util.plugin_abstract import IPlugin
import time

RESULT_TEXT = "Result_Text"

class ToolbarActionThread(QThread):
    def __init__(self, parent, old_text):
        super(ToolbarActionThread, self).__init__()
        self.parent = parent
        self.old_text = old_text

    def run(self):
        print("start_action")
        time.sleep(120)
        print("end_action")
        new_text = self.old_text + "\nLong Work Done"
        self.parent.sig.execute_action.emit({RESULT_TEXT: new_text})


class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.sig.execute_action.connect(self.execute_action)

    def get_toolbar_action(self, parent_window) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "example_action", "icons", self.plugin_manager.theme, "empty.png")
        action = QAction(QIcon(icon_path), "Long", parent_window)
        action.triggered.connect(self.do_long_work)
        return [action]

    def do_long_work(self):
        self.thread = ToolbarActionThread(self, self.plugin_manager.get_text())
        self.thread.start()

    def execute_action(self, values):
        self.plugin_manager.set_text(values[RESULT_TEXT])

    def get_name(self) -> str:
        return "Long"