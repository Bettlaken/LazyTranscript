import os
from typing import List

from PySide2.QtCore import QLocale, QSettings
from PySide2.QtGui import QIcon, QDoubleValidator, QValidator, QFont
from PySide2.QtWidgets import QAction, QWidget, QPlainTextEdit, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout
from src.util.plugin_abstract import IPlugin
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import src.util.const as c

# After the tutorial from:
# https://www.geeksforgeeks.org/python-text-summarizer/
# and
# https://becominghuman.ai/text-summarization-in-5-steps-using-nltk-65b21e352b65


class SummaryWidget(QWidget):

    def __init__(self, plugin_manager):
        super(SummaryWidget, self).__init__()
        self.plugin_manager = plugin_manager

        icon_path = os.path.join(c.ICON_PATH, "neutral", "quote.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Summary")

        self.settings = QSettings(c.SETTINGS_PATH, QSettings.IniFormat)
        self.font = QFont(self.settings.value(c.FONT, defaultValue="Arial", type=str))
        self.font.setPointSize(12)

        self.summary_text = QPlainTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(self.font)


        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.get_summary)

        self.threshold_value = 1.2
        self.threshold = QLineEdit(str(self.threshold_value))
        self.threshold.setFixedSize(40, 25)
        self.validator = QDoubleValidator()
        self.validator.setLocale(QLocale.English)
        self.threshold.setValidator(self.validator)
        self.threshold.textChanged.connect(self.threshold_changed)

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.refresh_btn)
        self.h_box.addWidget(self.threshold)

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.summary_text)
        self.v_box.addLayout(self.h_box)
        self.setLayout(self.v_box)
        self.resize(500, 500)

    def get_summary(self):
        if "de" in self.plugin_manager.get_language():
            language = "german"
        elif "en" in self.plugin_manager.get_language():
            language = "english"
        else:
            return

        text = self.plugin_manager.get_text()
        stop_words = set(stopwords.words(language))
        words = word_tokenize(text=text, language=language)

        # count word frequency
        freq = dict()
        for word in words:
            word = word.lower()
            if word in stop_words:
                continue
            if word in freq:
                freq[word] += 1
            else:
                freq[word] = 1

        sentences = sent_tokenize(text, language)
        sentence_freq = dict()

        # sum frequency of words in each sentence
        for word, freq in freq.items():
            for sentence in sentences:
                if word in sentence.lower():
                    if sentence in sentence_freq:
                        sentence_freq[sentence] += freq
                    else:
                        sentence_freq[sentence] = freq

        # calculate avg freq per word in sentence so long sentences dont have an advantage
        for sentence in sentences:
            sentence_freq[sentence] = sentence_freq[sentence] / len(sentence.split())

        # calc average word-frequency per sentence
        sum_sentece_freq = 0
        for sentence in sentence_freq:
            sum_sentece_freq += sentence_freq[sentence]

        avg = int(sum_sentece_freq / len(sentence_freq))

        # filter sentences that doesn't reach the threshold
        summary = ""
        for sentence in sentence_freq:
            if sentence_freq[sentence] > (self.threshold_value * avg):
                summary += " " + sentence

        self.summary_text.setPlainText(summary.strip())

    def threshold_changed(self):
        validator = self.threshold.validator()
        validator_state = validator.validate(self.threshold.text(), 0)[0]

        if validator_state == QValidator.Acceptable:
            color = '#006600'
            self.threshold_value = float(self.threshold.text())
        else:
            color = '#800000'

        self.threshold.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def show(self):
        super(SummaryWidget, self).show()
        self.get_summary()



class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.widget = SummaryWidget(plugin_manager)

    def get_toolbar_action(self, parent_window) -> List[QAction]:
        icon_path = os.path.join(c.PLUGIN_PATH, "summary", "icons", self.plugin_manager.theme, "sum.png")
        action = QAction(QIcon(icon_path), self.get_name(), parent_window)
        action.triggered.connect(self.show_sum)
        return [action]

    def show_sum(self):
        if self.widget.isVisible():
            self.widget.hide()
        else:
            self.widget.show()

    def get_name(self) -> str:
        return "Summary"