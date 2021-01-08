from typing import List

from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QAction

class PluginSignal(QObject):
    """Signals that can be used to send values back to the main thread

    create_button-signal contains the word, the postion and a dict with additional values.
    execute_action-signal contains a dict with value like the text or anything else.

    """

    create_button = Signal(str, int, dict)
    execute_action = Signal(dict)

class IPlugin():
    """Plug-in Interface.

    Use the plugin manager to get or edit the text or a specific words.

    """

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.sig = PluginSignal()

    def project_loaded(self):
        """Called when the project is successfully loaded."""
        pass

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        """Create the QPushButtons which should be displayed in the Word for Word list.

        To add the created buttons to the list, use the add_new_word_by_word_action method of the Plugin_Manager.

        Args:
          word: str: The current word
          word_meta_data: List[dict]: The meta_data from the word.
          word_pos: int:  The current word position

        """
        pass

    def get_toolbar_action(self, parent) -> List[QAction]:
        """Return here the QActions which should be displayed in the toolbar.

        Args:
          parent: The parent-window, necessary to hand over to the qactions.

        Returns:
          A List of QAction which will be displayed in the Toolbar.

        """
        return []

    def get_name(self) -> str:
        """Return here the plugin name"""
        return None


