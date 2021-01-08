from os import walk
from PySide2.QtCore import QSettings
from PySide2.QtGui import QKeySequence
from src.util.plugin_abstract import IPlugin
import src.util.const as c
import importlib.util as ilu
import os

class PluginManager():
    """Creates and manages the plugins.

    Serves as a bridge between the editor and the plugins.

    """

    def __init__(self, parent):
        self.parent = parent
        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.keyboard_settings = QSettings(c.KEYBOARD_SETTINGS_PATH, QSettings.IniFormat)
        self.theme = self.settings.value(c.THEME, defaultValue=c.THEME_D)
        self.get_keyboard_shortcuts()
        self.get_plugins()
        self.do_not_delete = [c.SAVE_KEY, c.WORD_BY_WORD_KEY_NEXT, c.FORWARD_KEY, c.PLAY_PAUSE_KEY, c.BACKWARDS_KEY, c.HELP_KEY, c.WORD_BY_WORD_KEY_PREV]

    def get_keyboard_shortcuts(self):
        """Saves the current occupied shortcuts in a list"""

        self.occupied_keys = []
        for key in self.keyboard_settings.allKeys():
            keyboard_value = self.keyboard_settings.value(key)
            if len(keyboard_value) != 0:
                self.occupied_keys.append(keyboard_value)

    def get_plugins(self):
        """Creates all Plugins and saves them in the plugin-list."""

        self.plugin_list = []
        for (dirpath, dirname, filenames) in walk(c.PLUGIN_PATH):
            for file in filenames:
                if c.PLUGIN_POST not in file or "__pycache__" in dirpath:
                    continue
                try:
                    module_path = os.path.join(dirpath, file)
                    temp_spec = ilu.spec_from_file_location(file.split(".")[0], module_path)
                    temp_module = ilu.module_from_spec(temp_spec)
                    temp_spec.loader.exec_module(temp_module)
                    temp_plugin = temp_module.Plugin(self)
                    if issubclass(type(temp_plugin), IPlugin):
                        self.plugin_list.append(temp_plugin)
                        print("Imported {} as a Plugin".format(file))
                except BaseException as e:
                    print("Error while importing {} with Exception {}".format(file, e))

    def get_plugin_licences(self):
        """Gets all used plugin-licences."""

        licences = {}
        for (dirpath, dirname, filenames) in walk(c.PLUGIN_PATH):
            if dirpath.lower().endswith("licences"):
                for filename in filenames:
                    licences[filename.split(".")[0]] = dirpath

        return licences

    def get_toolbar_actions(self, parent):
        """Queries all toolbar actions from the plugins.

        Handles the Keyboard-Shortcuts from this toolbar-actions and prevents overlapping.

        Args:
          parent: The Parent-Window.

        Returns:
          Returns list of the QActions from all plugins.
        """

        actions = []
        for plugin in self.plugin_list:
            plugin_actions = plugin.get_toolbar_action(parent)
            plugin_name = plugin.get_name()
            for action in plugin_actions:
                if action is None or plugin_name is None or not plugin_name:
                    continue
                key_name = plugin_name.upper().replace(" ", "_") + "_KEY"
                saved_key = self.keyboard_settings.value(key_name, defaultValue=None)
                plugin_shortcut = action.shortcut()
                if saved_key is None and not plugin_shortcut.isEmpty():
                    plugin_shortcut_upper = plugin_shortcut.toString().upper()
                    if plugin_shortcut_upper not in self.occupied_keys:
                        self.keyboard_settings.setValue(key_name, plugin_shortcut_upper)
                        self.occupied_keys.append(saved_key)
                    else:
                        self.keyboard_settings.setValue(key_name, "")
                    self.do_not_delete.append(key_name)
                if saved_key is not None:
                    action.setShortcut(QKeySequence(saved_key))
                actions.append(action)
        self.clear_keyboard_settings()
        return actions

    def clear_keyboard_settings(self):
        """Deletes all unused shortcuts from the keyboard settings."""

        all_keys = set(self.keyboard_settings.allKeys())
        to_delete = all_keys.difference(set(self.do_not_delete))
        for key in to_delete:
            print("removed", key)
            self.keyboard_settings.remove(key)

    def get_word_by_word_actions(self, word, meta_data, pos):
        """Queries all QPushButtons of the plugins.

        Args:
          word: str: The current word
          word_meta_data: List[dict]: The meta_data from the word.
          word_pos: int:  The current word position

        """

        for plugin in self.plugin_list:
            plugin.get_word_action(word, meta_data, pos)

    def project_loaded(self):
        """Calls the project_loaded method of all plugins."""

        for plugin in self.plugin_list:
            plugin.project_loaded()

    def add_new_word_by_word_action(self, btns, name, word, word_pos):
        """Adds a new Word-Action (QPushButton) to the editor word by word list.

        Args:
          btns: The QPushButtons from the plugin.
          name: The Name of the Buttons.
          word: The word for which these buttons are.
          word_pos: The position of the word.

        """

        btns = btns
        for btn in btns:
            btn.setShortcut(None)
        self.parent.add_new_word_by_word_action(btns, name, word, word_pos)


    def get_selection(self):
        """Gets the current selected word(s) in the editor.

        Returns:
          Selected word(s)

        """

        return self.parent.get_selection()

    def replace_selection(self, new_word):
        """Replaces the current selection in the editor.

        Args:
          new_word: the word(s) which should replace the current selection

        """

        self.parent.replace_selection(new_word)

    def get_text(self):
        """Returns the full text from the editor.

        Returns:
          The full text from the editor.

        """

        return self.parent.get_text()

    def set_text(self, new_text):
        """Sets the text in the editor with the given new_text.

        Args:
          new_text: The new text.

        """

        self.parent.set_text(new_text)

    def get_word_at(self, pos):
        """Gets a the word at the given position.

        Args:
          pos: Position of the desired word.

        Returns:
          The word at the position.
        """

        return self.parent.get_word_at(pos)

    def set_word_at(self, word, pos, replace_old):
        """Sets the word at a given position.

        Args:
          word: The word which should be set.
          pos: The position on which the word should be set.
          replace_old: true: replace the old word on the positon, false: set it before.

        """

        self.parent.set_word_at(word, pos, replace_old)

    def get_setting(self, key, default):
        """Get a specific setting.

        Args:
          key: The settings-key
          default: The default value if there is no setting for the key.

        Returns:
          The settings value for the given key or the default if nothing is there.
        """

        return self.settings.value(key, defaultValue=default)

    def get_language(self):
        """Returns the language of the current project.

        Returns:
            The language of the current project.

        """

        return self.parent.get_language()

    def set_hint_text(self, text):
        """Sets the hint text (left bottom corner) in the editor.

        Args:
          text: The Hint text.

        """

        self.parent.set_hint_text(text)

    def set_text_with_line_breaks(self, new_text):
        """Sets the Text in the editor but tries to restore the given linebreaks.

        Args:
          new_text: The new text.

        """

        self.parent.set_text_with_line_breaks(new_text)

    def get_project_folder_path(self):
        """Get the current project folder path

        Returns:
          Project folder path.

        """

        return self.parent.get_project_folder_path()