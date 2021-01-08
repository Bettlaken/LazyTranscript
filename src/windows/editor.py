from PySide2.QtCore import QSize, QUrl, QSettings
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from src.util import file_util
from src.util.plugin_manager import PluginManager
from src.windows.text_module import TextModuleWindow
from src.windows.settings import SettingsWindow
from src.windows.licence import LicenceWindow
from src.util.time_util import create_time_string
from src.util.time_util import convert_ms
from datetime import datetime
import os
import src.util.const as c

class HearButton(QPushButton):
    """Class for the hear again buttons in the word by word editing list."""

    def __init__(self, parent, meta_data):
        super(HearButton, self).__init__()
        self.parent = parent
        self.start_time = max(meta_data.get(c.START_TIME) * 1000 - 1000, 0)
        self.end_time = meta_data.get(c.END_TIME) * 1000
        self.setText(meta_data.get(c.WORD) + " (" + convert_ms(meta_data.get(c.START_TIME) * 1000) + ")")
        self.clicked.connect(self.on_click)

    def on_click(self):
        """Calls the hear_again method of the editor widget."""

        self.parent.start_hear_again(self.start_time, self.end_time)


class EditorWidget(QWidget):
    """Widget which contain the editor."""

    def __init__(self, plugin_manager):
        super(EditorWidget, self).__init__()
        os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
        self.plugin_manager = plugin_manager

        #parent layout
        self.v_box = QVBoxLayout()
        self.h_box = QHBoxLayout()
        # parent splitter for the text and numbers
        self.text_h_box = QSplitter(Qt.Horizontal)
        self.text_h_box.splitterMoved.connect(self.on_text_changed)

        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.keyboard_settings = QSettings(c.KEYBOARD_SETTINGS_PATH, QSettings.IniFormat)
        self.theme = self.settings.value(c.THEME, defaultValue=c.THEME_D)

        # font settings
        self.font = QFont(self.settings.value(c.FONT, defaultValue="Arial", type=str))
        self.font.setPointSize(self.settings.value(c.FONT_SIZE, defaultValue=16, type=int))

        # the text widget itself
        self.text = QPlainTextEdit()
        self.text.setFont(self.font)
        self.text.textChanged.connect(self.on_text_changed)
        self.text.setFocusPolicy(Qt.StrongFocus)

        # the number text widget to show the row numbers
        self.numbers = QPlainTextEdit()
        self.numbers.setFont(self.font)
        self.numbers.setReadOnly(True)
        self.numbers.setMinimumWidth(20)
        self.numbers.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.numbers.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.numbers.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.numbers.setFocusPolicy(Qt.NoFocus)
        self.numbers.setFrameStyle(QFrame.NoFrame)
        self.numbers.setStyleSheet("background-color: rgba(0,0,0,0%)")

        # sync the text widget and number widget
        self.text_bar = self.text.verticalScrollBar()
        self.number_bar = self.numbers.verticalScrollBar()
        #self.number_bar.valueChanged.connect(self.text_bar.setValue)
        self.text_bar.valueChanged.connect(self.number_bar.setValue)

        # add them into their layout
        self.text_h_box.addWidget(self.numbers)
        self.text_h_box.addWidget(self.text)
        self.text_h_box.setSizes([10, 700])

        # layout which holds the media controls in the bottom
        self.media_controls = QHBoxLayout()
        self.media_controls_settings = QVBoxLayout()
        self.media_controls_slider_h_box = QHBoxLayout()

        # direct player controls
        self.btn_size = 75
        self.play_icon = QIcon(os.path.join(c.ICON_PATH, self.theme, "play.png"))
        self.pause_icon = QIcon(os.path.join(c.ICON_PATH, self.theme, "pause.png"))
        self.play_btn = QPushButton(icon = self.play_icon)
        self.play_btn.clicked.connect(self.on_play)
        self.play_btn.setFixedSize(self.btn_size, self.btn_size)
        self.play_btn.setIconSize(QSize(self.btn_size, self.btn_size))
        self.play_btn.setFlat(True)
        self.play_btn.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.PLAY_PAUSE_KEY, defaultValue="")))
        self.forward_btn = QPushButton(icon = QIcon(os.path.join(c.ICON_PATH, self.theme,"forward.png")))
        self.forward_btn.clicked.connect(self.on_forward)
        self.forward_btn.setFixedSize(self.btn_size, self.btn_size)
        self.forward_btn.setIconSize(QSize(self.btn_size, self.btn_size))
        self.forward_btn.setFlat(True)
        self.forward_btn.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.FORWARD_KEY, defaultValue="")))
        self.backward_btn = QPushButton(icon = QIcon(os.path.join(c.ICON_PATH, self.theme,"backward.png")))
        self.backward_btn.clicked.connect(self.on_backward)
        self.backward_btn.setFixedSize(self.btn_size, self.btn_size)
        self.backward_btn.setIconSize(QSize(self.btn_size, self.btn_size))
        self.backward_btn.setFlat(True)
        self.backward_btn.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.BACKWARDS_KEY, defaultValue="")))

        # add them to the layout
        self.media_controls.addStretch()
        self.media_controls.addWidget(self.backward_btn)
        self.media_controls.addWidget(self.play_btn)
        self.media_controls.addWidget(self.forward_btn)
        self.media_controls.addStretch(4)

        # slider which shows the current time
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.sliderMoved.connect(self.on_time_slider_moved)

        # label on the right of the slider, which shows the current time
        self.time_label = QLabel("00:00/00:00")
        self.media_controls_slider_h_box.addWidget(self.time_slider)
        self.media_controls_slider_h_box.addWidget(self.time_label)

        # icons for the other sliders
        self.vol_icon = QIcon(os.path.join(c.ICON_PATH, self.theme, "volume.png")).pixmap(QSize(32,32))
        self.rate_icon = QIcon(os.path.join(c.ICON_PATH, self.theme, "playbackrate.png")).pixmap(QSize(32,32))
        self.rewind_icon = QIcon(os.path.join(c.ICON_PATH, self.theme, "time.png")).pixmap(QSize(32,32))

        # display the icons through labels
        self.vol_icon_label = QLabel()
        self.vol_icon_label.setPixmap(self.vol_icon)
        self.rate_icon_label = QLabel()
        self.rate_icon_label.setPixmap(self.rate_icon)
        self.rewind_rewind_label = QLabel()
        self.rewind_rewind_label.setPixmap(self.rewind_icon)

        # init of the other sliders
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.sliderMoved.connect(self.on_vol_slider_moved)
        self.vol_slider.setFixedWidth(250)
        self.vol_slider.setRange(1, 100)
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.sliderMoved.connect(self.on_rate_slider_moved)
        self.rate_slider.setFixedWidth(250)
        self.rate_slider.setRange(1, 20)
        self.rewind_time = 10
        self.rewind_slider = QSlider(Qt.Horizontal)
        self.rewind_slider.sliderMoved.connect(self.on_rewind_slider_moved)
        self.rewind_slider.setFixedWidth(250)
        self.rewind_slider.setRange(1, 60)
        self.rewind_slider.setValue(self.rewind_time)

        # labels for the values
        self.vol_label = QLabel()
        self.rate_label = QLabel()
        self.rewind_label = QLabel()

        # create hbox for each of the three sliders
        self.vol_h_box = QHBoxLayout()
        self.vol_h_box.addWidget(self.vol_label)
        self.vol_h_box.addWidget(self.vol_slider)
        self.vol_h_box.addWidget(self.vol_icon_label)

        self.rate_h_box = QHBoxLayout()
        self.rate_h_box.addWidget(self.rate_label)
        self.rate_h_box.addWidget(self.rate_slider)
        self.rate_h_box.addWidget(self.rate_icon_label)

        self.rewind_h_box = QHBoxLayout()
        self.rewind_h_box.addWidget(self.rewind_label)
        self.rewind_h_box.addWidget(self.rewind_slider)
        self.rewind_h_box.addWidget(self.rewind_rewind_label)

        # group them together in a vlayout
        self.media_controls_settings.addLayout(self.vol_h_box)
        self.media_controls_settings.addLayout(self.rewind_h_box)
        self.media_controls_settings.addLayout(self.rate_h_box)

        # add this layout to the layout which already contains the buttons
        self.media_controls.addLayout(self.media_controls_settings)

        self.word_by_word_actions = QListWidget()
        self.word_by_word_actions.setMaximumWidth(150)


        self.h_box.addWidget(self.text_h_box)
        self.h_box.addWidget(self.word_by_word_actions)

        # group all ungrouped layouts and widgets to the parent layout
        self.v_box.addLayout(self.h_box, 10)
        self.v_box.addLayout(self.media_controls_slider_h_box, 1)
        self.v_box.addLayout(self.media_controls, 1)

        # set parent layout
        self.setLayout(self.v_box)

        # init media_player
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_widget.setGeometry(200, 200, 500, 300)
        self.video_widget.setWindowTitle("Output")
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.positionChanged.connect(self.on_position_change)
        self.media_player.durationChanged.connect(self.on_duration_change)
        self.vol_slider.setValue(self.media_player.volume())
        self.rate_slider.setValue(int(self.media_player.playbackRate() * 10))

        self.on_vol_slider_moved(self.media_player.volume())
        self.on_rate_slider_moved(self.media_player.playbackRate() * 10)
        self.on_rewind_slider_moved(self.rewind_time)

        self.activate_text_modules = False
        self.get_text_modules()

        self.text_option_on = QTextOption()
        self.text_option_on.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)

        self.text_option_off = QTextOption()

        self.transcription_meta_data = None
        self.word_pos = -1
        self.word_start_time = None
        self.word_end_time = None

        self.tcf_highlight = QTextCharFormat()
        self.tcf_highlight.setBackground(Qt.red)
        self.tcf_normal = QTextCharFormat()
        self.tcf_normal.setBackground(Qt.transparent)

        self.show_empty_buttons = self.settings.value(c.SHOW_EMPTY_BUTTONS, defaultValue=True, type=bool)

    def on_position_change(self, position):
        """Is executed when media is played (position is changed)

        Args:
          position: Current position (ms) of the media player.

        """

        self.time_slider.setValue(position)
        self.time_label.setText(create_time_string(position, self.media_player.duration()))

        if self.word_end_time is None:
            return

        if position > self.word_end_time:
            self.on_play()
            self.word_start_time = None
            self.word_end_time = None

    def on_duration_change(self, duration):
        """Is executed when duration of the media changes.

        Args:
          duration: duration of the media.

        """

        self.time_slider.setRange(0, duration)
        self.time_label.setText(create_time_string(0, self.media_player.duration()))

    def on_time_slider_moved(self, value):
        """Is executed when the time slider was moved.

        Args:
          value: current value of the slider.

        """

        self.media_player.setPosition(value)

    def on_vol_slider_moved(self, value):
        """Is executed when the volume slider is moved.

        Args:
          value: current value of the slider.

        """

        self.media_player.setVolume(value)
        self.vol_label.setText(str(value) + "%")

    def on_rate_slider_moved(self, value):
        """Is executed when the rate slider is moved.

        Args:
          value: current value of the slider.

        """

        self.media_player.setPlaybackRate(value / 10)
        self.rate_label.setText(str(value / 10) + "x")

    def on_rewind_slider_moved(self, value):
        """Is executed when the rewind slider is moved.

        Args:
          value: current value of the slider.

        """

        self.rewind_time = value
        self.rewind_label.setText(str(value) + "s")

    def on_play(self):
        """Is executed when the play or pause button is pressed."""

        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.play_icon)

        else:
            self.media_player.play()
            self.play_btn.setIcon(self.pause_icon)

    def on_forward(self):
        """Is executed when the forward button is pressed."""

        self.media_player.setPosition(self.media_player.position() + self.rewind_time * 1000)

    def on_backward(self):
        """Is executed when the backward button is pressed."""

        self.media_player.setPosition(self.media_player.position() - self.rewind_time * 1000)

    def on_text_changed(self):
        """Is executed when the text changed

        Calculates the line numbers and sets the text modules if activated.

        """

        lines = int(self.text.document().documentLayout().documentSize().height())
        self.numbers.setPlainText("")
        text = ""
        for i in range(1, lines + 1):
            text = text + str(i) + "\n"

        self.numbers.setPlainText(text)
        self.number_bar.setSliderPosition(self.text_bar.sliderPosition())

        new_text = self.text.toPlainText()

        if self.activate_text_modules == True:
            for key in self.text_modules.keys():
                to_replace = " " + key + " "
                to_replace_with = " " + self.text_modules[key] + " "
                new_text = new_text.replace(to_replace, to_replace_with)

        if self.text.toPlainText() != new_text:
            old_pos = self.text.textCursor().position()
            self.text.setPlainText(new_text)
            cursor = self.text.textCursor()
            cursor.setPosition(old_pos, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord)
            cursor.movePosition(QTextCursor.NextCharacter)
            self.text.setTextCursor(cursor)

    def show_video(self):
        """Shows or hides the video feed."""

        if self.video_widget.isVisible():
            self.video_widget.hide()
        else:
            self.video_widget.show()

    def open_project(self, project_folder_path):
        """Opens a project.

        Args:
          project_folder_path: folder of the project which should be opened.

        """
        self.project_folder_path = project_folder_path
        self.media_file = file_util.get_file(self.project_folder_path, c.CON_COPY_POSTFIX)
        if self.media_file is None:
            self.hide()
            return
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_file)))

        self.transcription_path = file_util.get_file(self.project_folder_path, c.TRANSCRIPTION)
        if self.transcription_path is None:
            self.hide()
            return
        with open(self.transcription_path, 'r') as f:
            text = f.read()
        self.text.setPlainText(text)
        self.transcription_meta_data = file_util.get_value_from_shelve(self.project_folder_path, c.TRANSCRIPTION_META_DATA)
        print(self.transcription_meta_data)

    def change_font(self, new_font, new_size):
        """Changes the font.

        Args:
          new_font: Name of the new font.
          new_size: New font size.

        """
        self.font = QFont(new_font)
        self.font.setPointSize(int(new_size))
        self.text.setFont(self.font)
        self.numbers.setFont(self.font)
        self.settings.setValue(c.FONT_SIZE, int(new_size))
        self.settings.setValue(c.FONT, new_font)

    def get_text_modules(self):
        """Gets the saved text_modules from the settings."""

        self.text_modules = self.settings.value(c.TEXT_MODULES, defaultValue={})

    def show_special_characters(self, bol):
        """Displays the special characters.

        Args:
          bol: true or false.

        """

        if bol:
            self.text.document().setDefaultTextOption(self.text_option_on)
        else:
            self.text.document().setDefaultTextOption(self.text_option_off)

    def on_word_by_word(self):
        """Selects the next or first word in the on word by word editing mode.

        For that purpose th word_postion is increased and the next word is marked via the textcursor.
        If everything works correctly the population of the list will be started.

        """

        self.word_pos += 1
        #if self.media_player.state() == QMediaPlayer.PlayingState:
        #    return

        if self.word_pos > len(self.text.toPlainText().split()) - 1:
            self.reset_word_by_word()
            return

        cursor = self.text.textCursor()
        if self.word_pos == 0:
            self.show_empty_buttons = self.settings.value(c.SHOW_EMPTY_BUTTONS, defaultValue=True, type=bool)
            cursor.setPosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            self.text.setEnabled(False)
        else:
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)

        self.text.setTextCursor(cursor)

        selected_word = cursor.selectedText()

        if not selected_word:
            self.word_pos -= 1
            self.on_word_by_word()
            return

        # change to find all meta data
        meta_data_with_word = self.find_meta_data(selected_word)

        self.populate_word_actions(selected_word, meta_data_with_word)

    def on_word_by_word_prev(self):
        """Same as word for word but selects to the previous word."""

        if self.word_pos < 1:
            return

        self.word_pos -= 2

        cursor = self.text.textCursor()
        count = 0
        cursor.setPosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        while count < self.word_pos:
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
            count += 1
        self.text.setTextCursor(cursor)
        self.on_word_by_word()

    def reset_word_by_word(self):
        """Resets the word by word editing mode and goes back to the normal editing."""

        self.word_pos = -1
        self.play_to = -1
        self.text.setEnabled(True)
        self.word_by_word_actions.clear()
        cleaned = self.text.textCursor()
        cleaned.clearSelection()
        self.text.setTextCursor(cleaned)

    def populate_word_actions(self, selected, word_meta_data):
        """Calls the plugin_manager to get alle the word for word buttons and initalize the hear again buttons.

        Args:
          selected: The selected word.
          word_meta_data: The meta_data fr the word.

        """

        self.word_by_word_actions.clear()
        if self.word_pos == len(self.text.toPlainText().split()):
            return

        self.plugin_manager.get_word_by_word_actions(selected, word_meta_data, self.word_pos)

        btns = []
        for meta_data in word_meta_data:
            media_btn = HearButton(self, meta_data)
            btns.append(media_btn)
        self.add_new_word_by_word_action(btns, "Hear again", selected, self.word_pos)

    def add_new_word_by_word_action(self, btns, name, word, word_pos):
        """Adds a new word by word action.

        Args:
          btns: The buttons to add.
          name: The (plugin-)name of the buttons.
          word: The word for which these buttons are.
          word_pos: The word position.

        """

        if not self.show_empty_buttons and len(btns) == 0:
            return

        if self.word_pos != word_pos:
            print("old item", word, word_pos, self.word_pos)
            return

        group_item = QListWidgetItem()
        group_item.setFlags(Qt.ItemIsSelectable)
        label = QLabel(name)
        label.setFixedSize(self.word_by_word_actions.width() - 15, 30)
        label.setContentsMargins(5, 0, 0, 0)
        label.setWordWrap(True)
        group_item.setSizeHint(label.size())
        self.word_by_word_actions.addItem(group_item)
        self.word_by_word_actions.setItemWidget(group_item, label)

        for btn in btns:
            btn.setFixedSize(self.word_by_word_actions.width() - 15, 30)
            item = QListWidgetItem()
            item.setSizeHint(btn.size())
            item.setFlags(Qt.ItemIsSelectable)
            self.word_by_word_actions.addItem(item)
            self.word_by_word_actions.setItemWidget(item, btn)

    def find_meta_data(self, word):
        """Gets all the meta_data for the given word.

        Args:
          word: The word for which the meta_data should be found.

        Returns:
          The meta_data
        """

        meta_data_with_word = []

        for m_d in self.transcription_meta_data:
            if m_d.get(c.WORD) == word.lower():
                meta_data_with_word.append(m_d)

        return meta_data_with_word

    def replace_selection(self, new_word):
        """Replace the selection with the given word

        Args:
          new_word: The replacement.

        """

        cursor = self.text.textCursor()
        old_cursor_pos = cursor.position()

        cursor.insertText(new_word)
        cursor.setPosition(old_cursor_pos, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.MoveAnchor)
        self.text.setTextCursor(cursor)
        self.word_by_word_actions.clear()

    def get_selection(self):
        """Returns the current selection

        Returns:
          The current selection.

        """

        return self.text.textCursor().selectedText()

    def get_text(self):
        """Returns the current text

        Returns:
          The current text.

        """

        return self.text.toPlainText()

    def set_text(self, new_text, restore_line_breaks = False):
        """Replace the text with the new text.

        Args:
          new_text: The new text.
          restore_line_breaks: If true, tries to restore the line breaks. (Default value = False)

        """

        cursor = self.text.textCursor()
        old_cursor_pos = cursor.position()

        if restore_line_breaks:
            self.set_text_with_line_breaks(new_text)
        else:
            self.text.setPlainText(new_text)

        cursor.setPosition(old_cursor_pos, QTextCursor.MoveAnchor)
        self.text.setTextCursor(cursor)

    def get_word_at(self, pos):
        """Returns the word at the given position.

        Args:
          pos: The position of the word.

        Returns:
          The word at the given position.

        """

        text = self.text.toPlainText().strip().split()

        if pos < 0 or pos > len(text):
            return None

        return text[pos%len(text)]

    def set_word_at(self, word, pos, replace_old):
        """Sets the word at the given position.

        Args:
          word: The replacement.
          pos: The position.
          replace_old: If true, the old word at the position will be replaced, otherwise the word will be set before the old word.

        """

        old_word = self.get_word_at(pos)
        cursor = self.text.textCursor()
        cursor_pos = cursor.position()

        if pos < 0:
            self.text.setPlainText(word + " " + self.text.toPlainText())
            cursor.setPosition(cursor_pos, QTextCursor.MoveAnchor)
            self.text.setTextCursor(cursor)
            return

        text = self.text.toPlainText().strip().split()
        if replace_old and pos < len(text):
            if word:
                text[pos] = word
            else:
                text.pop(pos)
        else:
            text.insert(pos, word)

        text = " ".join(text)
        self.set_text_with_line_breaks(text)

        cursor_pos += len(word)

        if replace_old:
            cursor_pos -= len(old_word)
            if not word:
                cursor_pos -= 1
        else:
            cursor_pos += 1

        words_to_cursor_pos = self.text.toPlainText()[:cursor_pos].split()
        self.word_pos = len(words_to_cursor_pos) - 1

        cursor.setPosition(cursor_pos, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.MoveAnchor)
        self.text.setTextCursor(cursor)

    def find_line_breaks(self):
        """Returns the lien breaks in the text.

        Returns:
          The positions of the linebreaks

        """

        found = []
        start = 0
        text = self.text.toPlainText()
        while True:
            start = text.find("\n", start)
            if start == -1:
                return found
            found.append(start)
            start += len("\n")

    def set_text_with_line_breaks(self, text):
        """Sets the text with linebreaks.

        Args:
          text: the new text.

        """

        line_breaks = self.find_line_breaks()
        for n in line_breaks:
            text = text[:n+1] + "\n" + text[n+1:]

        text = text.replace(" \n", "\n")
        text = text.replace("\n ", "\n")
        self.text.setPlainText(text)

    def insert_time_stamp(self):
        """Inserts the current timestamp at the current cursor position."""

        cursor = self.text.textCursor()
        time = "[" + convert_ms(self.media_player.position()) + "]"
        cursor.insertText(time)

    def start_hear_again(self, start_time, end_time):
        """Starts the audio for the specific word from the hear again button.

        Args:
          start_time: When to start the audio.
          end_time: When to end the audio.

        """

        if self.media_player.state() == QMediaPlayer.PlayingState:
            return
        self.media_player.pause()
        self.word_start_time = start_time
        self.word_end_time = end_time
        self.media_player.setPosition(self.word_start_time)
        self.on_play()

class EditorWindow(QMainWindow):
    """Widget which contain the editor."""

    def __init__(self, window_handler):
        super(EditorWindow, self).__init__()
        self.plugin_manager = PluginManager(self)

        self.setGeometry(400, 200, 1280, 720)
        self.widget = EditorWidget(self.plugin_manager)

        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.keyboard_settings = QSettings(c.KEYBOARD_SETTINGS_PATH, QSettings.IniFormat)
        self.theme = self.settings.value(c.THEME, defaultValue=c.THEME_D)

        self.init_menu_and_toolbar()
        self.setCentralWidget(self.widget)
        self.window_handler = window_handler

        self.last_saved = None

    def init_menu_and_toolbar(self):
        """Initialize the menu- and toolbar"""

        self.menu = self.menuBar()

        self.file_menu = self.menu.addMenu("File")

        self.file_menu_new = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "new.png")), "New", self)
        self.file_menu_new.triggered.connect(self.new_project)
        self.file_menu_open = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "open.png")), "Open", self)
        self.file_menu_open.triggered.connect(self.open_project_w_file_picker)
        self.file_menu_save = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "save.png")), "Save", self)
        self.file_menu_save.setShortcut(QKeySequence(self.keyboard_settings.value(c.SAVE_KEY, defaultValue="")))
        self.file_menu_save.triggered.connect(self.save_project)

        self.file_menu.addAction(self.file_menu_new)
        self.file_menu.addAction(self.file_menu_open)
        self.file_menu.addAction(self.file_menu_save)

        self.edit_menu = self.menu.addMenu("Edit")

        self.edit_menu_undo = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "undo.png")), "Undo", self)
        self.edit_menu_undo.triggered.connect(self.undo)
        self.edit_menu_undo.setShortcut(QKeySequence("CTRL+Z"))

        self.edit_menu_redo = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "redo.png")),"Redo", self)
        self.edit_menu_redo.triggered.connect(self.redo)
        self.edit_menu_redo.setShortcut(QKeySequence("CTRL+Shift+Z"))

        self.edit_menu_copy = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "copy.png")),"Copy", self)
        self.edit_menu_copy.triggered.connect(self.copy)
        self.edit_menu_copy.setShortcut(QKeySequence("CTRL+C"))

        self.edit_menu_paste = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "paste.png")),"Paste", self)
        self.edit_menu_paste.triggered.connect(self.paste)
        self.edit_menu_paste.setShortcut(QKeySequence("CTRL+V"))

        self.edit_menu.addAction(self.edit_menu_undo)
        self.edit_menu.addAction(self.edit_menu_redo)
        self.edit_menu.addAction(self.edit_menu_copy)
        self.edit_menu.addAction(self.edit_menu_paste)

        self.settings_menu = self.menu.addMenu("Settings")
        self.settings_menu_open = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "settings.png")), "Open Settings", self)
        self.settings_menu_open.triggered.connect(self.open_settings)
        self.settings_menu.addAction(self.settings_menu_open)

        self.settings_menu_text = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "receipt.png")), "Text modules", self)
        self.settings_menu_text.triggered.connect(self.open_text_modules)
        self.settings_menu.addAction(self.settings_menu_text)

        self.help_menu = self.menu.addMenu("Help")
        self.help_menu_open = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "help.png")), "Open Help", self)
        self.help_menu_open.triggered.connect(self.open_help)
        self.help_menu_open.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.HELP_KEY, defaultValue="")))
        self.help_menu.addAction(self.help_menu_open)

        self.help_menu_licence = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "snippet.png")), "Licences", self)
        self.help_menu_licence.triggered.connect(self.open_licences)
        self.help_menu.addAction(self.help_menu_licence)

        self.setMenuBar(self.menu)

        self.show_video = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "video.png")), "Open-Video", self)
        self.show_video.triggered.connect(self.widget.show_video)

        self.activate_tm = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "receipt.png")), "Activate Text modules", self)
        self.activate_tm.setCheckable(True)
        self.activate_tm.triggered.connect(self.activate_text_modules)

        self.show_chars = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "format.png")), "Show special Characters", self)
        self.show_chars.setCheckable(True)
        self.show_chars.triggered.connect(self.show_special_characters)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.addAction(self.file_menu_open)
        self.toolbar.addAction(self.file_menu_save)
        self.toolbar.addAction(self.show_video)
        self.toolbar.addAction(self.activate_tm)
        self.toolbar.addAction(self.show_chars)

        self.word_by_word_prev = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "prev.png")), "Word by word prev", self)
        self.word_by_word_prev.triggered.connect(self.on_word_by_word_prev)
        self.word_by_word_prev.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.WORD_BY_WORD_KEY_PREV, defaultValue="")))
        self.toolbar.addAction(self.word_by_word_prev)

        self.word_by_word_next = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "next.png")), "Word by word next", self)
        self.word_by_word_next.triggered.connect(self.on_word_by_word)
        self.word_by_word_next.setShortcut(QKeySequence().fromString(self.keyboard_settings.value(c.WORD_BY_WORD_KEY_NEXT, defaultValue="")))
        self.toolbar.addAction(self.word_by_word_next)

        self.time_stamp = QAction(QIcon(os.path.join(c.ICON_PATH, self.theme, "timestamp.png")), "Insert Timestamp", self)
        self.time_stamp.triggered.connect(self.insert_time_stamp)
        self.toolbar.addAction(self.time_stamp)

        for action in self.plugin_manager.get_toolbar_actions(self):
            self.toolbar.addAction(action)

        self.font_box = QComboBox()
        self.fonts = QFontDatabase().families()
        self.font_box.addItems(self.fonts)
        self.font_box.setCurrentIndex(self.fonts.index(QFontInfo(self.widget.font).family()))
        self.font_box.currentIndexChanged.connect(self.on_font_change)

        self.font_size = QComboBox()
        self.sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"]
        self.font_size.addItems(self.sizes)
        self.font_size.setCurrentIndex(6)
        self.font_size.currentIndexChanged.connect(self.on_font_change)

        self.toolbar.addWidget(self.font_box)
        self.toolbar.addWidget(self.font_size)

        self.status_bar = QStatusBar()
        self.language_label = QLabel()
        self.project_folder_path_label = QLabel()
        self.hint_label = QLabel()
        self.hint_label.setMaximumWidth(300)
        self.status_bar.addPermanentWidget(self.project_folder_path_label)
        self.status_bar.addPermanentWidget(self.language_label)
        self.status_bar.addWidget(self.hint_label)
        self.setStatusBar(self.status_bar)

        self.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))

        self.text_modules_window = TextModuleWindow(self)
        self.settings_window = SettingsWindow()
        self.licence_window = LicenceWindow(self.plugin_manager)

    def new_project(self):
        """Opens the create new project window."""

        self.window_handler.open_create_new_project_window()

    def open_project_w_file_picker(self):
        """Opens a folder dialog to open another project."""

        msg_box = QMessageBox()
        msg_box.setText("Do you really want to open a new Project? \nProject last saved on: " + (
            self.last_saved if self.last_saved is not None else "never"))
        msg_box.setWindowTitle("Open Project")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))

        return_val = msg_box.exec_()
        if return_val == QMessageBox.Cancel:
            return

        folder_path = QFileDialog.getExistingDirectory(self, "Choose a Project Folder")
        if folder_path == "":
            return
        self.open_project(os.path.normpath(folder_path))

    def open_project(self, project_folder_path):
        """Opens the choosen project.

        Args:
          project_folder_path: The folder of the project which should be opened.

        """

        self.project_folder_path = project_folder_path
        self.widget.open_project(self.project_folder_path)
        self.project_folder_path_label.setText(self.project_folder_path)
        self.language = file_util.get_value_from_shelve(self.project_folder_path, c.LANGUAGE)
        self.language_label.setText(self.language)
        self.setWindowTitle(os.path.basename(self.project_folder_path))
        self.plugin_manager.project_loaded()

    def save_project(self):
        """Saves the current transcription."""

        file_util.write_text_file(self.project_folder_path, self.widget.text.toPlainText(), c.TRANSCRIPTION)
        self.last_saved = datetime.now().strftime("%H:%M:%S")
        self.setWindowTitle(os.path.basename(self.project_folder_path) + " - last saved on: " + self.last_saved)

    def undo(self):
        self.widget.text.undo()

    def redo(self):
        self.widget.text.redo()

    def copy(self):
        self.widget.text.copy()

    def paste(self):
        self.widget.text.paste()

    def open_settings(self):
        """Opens the settings window."""

        if self.settings_window.isVisible():
            self.settings_window.hide()
        else:
            self.settings_window.show()

    def open_help(self):
        """Opens the manual.pdf in the installed pdf viewer."""

        guide_path = os.path.join(c.ASSETS_PATH, "docs", "manual.pdf")
        os.system(guide_path)

    def on_font_change(self):
        """Calls the change font method of the widget."""

        self.widget.change_font(self.font_box.currentText(), self.font_size.currentText())

    def open_text_modules(self):
        """Opens the text modules window."""

        if self.text_modules_window.isVisible():
            self.text_modules_window.hide()
        else:
            self.text_modules_window.show()

    def on_text_modules_change(self):
        """If the text_modules change, then update then in the widget."""

        self.widget.get_text_modules()

    def activate_text_modules(self):
        """Deactivates or activates the text_modules."""

        self.widget.activate_text_modules = self.activate_tm.isChecked()

    def show_special_characters(self):
        """Deactivates or activates the special characters."""

        self.widget.show_special_characters(self.show_chars.isChecked())

    def on_word_by_word(self):
        """Is executed when the on word by word button is pressed."""
        self.widget.on_word_by_word()

    def on_word_by_word_prev(self):
        """Is executed when the on prev. word by word button is pressed."""
        self.widget.on_word_by_word_prev()

    def get_selection(self):
        """Returns the current selection

        Returns:
         Current selection.

        """

        return self.widget.get_selection()

    def replace_selection(self, new_word):
        """Replace the current selection

        Args:
          new_word: the replacement.

        """

        self.widget.replace_selection(new_word)

    def get_text(self):
        """Returns the current text.

        Returns:
         The current text.

        """

        return self.widget.get_text()

    def set_text(self, new_text):
        """Sets the new_text in the editor widget.

        Args:
          new_text: The new text.

        """

        self.widget.set_text(new_text)

    def get_word_at(self, pos):
        """Gets the word at a specific position.

        Args:
          pos: The position of the word.

        Returns:
         The word at this position.

        """

        return self.widget.get_word_at(pos)

    def set_word_at(self, word, pos, replace_old):
        """Sets the word at the given position.

        Args:
          word: The replacement.
          pos: The position to place the word.
          replace_old: True if the old one should be replaced, false if the word is should be set before the other word.

        """

        self.widget.set_word_at(word, pos, replace_old)

    def open_licences(self):
        """Opens the licence window."""

        if self.licence_window.isVisible():
            self.licence_window.hide()
        else:
            self.licence_window.show()

    def add_new_word_by_word_action(self, btns, name, word, word_pos):
        """Adds a new Word-Action (QPushButton) to the editor word by word list.

        Args:
          btns: The QPushButtons from the plugin.
          name: The Name of the Buttons.
          word: The word for which these buttons are.
          word_pos: The position of the word.

        """

        self.widget.add_new_word_by_word_action(btns, name, word, word_pos)

    def get_language(self):
        """Returns the language of the current project.

        Returns:
            The language of the current project.

        """

        return self.language

    def keyPressEvent(self, key_event: QKeyEvent):
        """Catches the Keypress-Events.

        In this case, if the key is esc then the word by word editing mode will be closed.

        Args:
          key_event: QKeyEvent: The key event

        """

        super(EditorWindow, self).keyPressEvent(key_event)
        if key_event.key() == Qt.Key_Escape:
            self.widget.reset_word_by_word()

    def set_hint_text(self, text):
        """Sets the hint text (left bottom corner) in the editor.

        Args:
          text: The Hint text.

        """

        self.hint_label.setText(text)

    def set_text_with_line_breaks(self, text):
        """Sets the Text in the editor but tries to restore the given linebreaks.

        Args:
          new_text: The new text.

        """

        self.widget.set_text_with_line_breaks(text)

    def insert_time_stamp(self):
        """Insert a timestamp at the current cursor position."""

        self.widget.insert_time_stamp()

    def get_project_folder_path(self):
        """Get the current project folder path

        Returns:
          Project folder path.

        """

        return self.project_folder_path

    def closeEvent(self, event):
        """Catches the close event. Shows a message if the programm should really be closed.

        Args:
          event: the close event.

        """

        msg_box = QMessageBox()
        msg_box.setText("Do you really want to close this window? \nProject last saved on: " + (self.last_saved if self.last_saved is not None else "never"))
        msg_box.setWindowTitle("Close LazyTranscript")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setWindowIcon(QIcon(os.path.join(c.ICON_PATH, c.THEME_NEUTRAL, "quote.png")))

        return_val = msg_box.exec_()
        if return_val == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication()
    window = EditorWindow()
    window.show()
    app.exec_()