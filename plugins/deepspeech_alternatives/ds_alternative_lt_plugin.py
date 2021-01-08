from os import listdir
from os.path import isfile, join
from typing import List
from PySide2.QtCore import QThread, QObject, Signal
from PySide2.QtWidgets import QPushButton
from src.util import file_util
from src.util.plugin_abstract import IPlugin
from deepspeech import Model
from pydub import AudioSegment
from src.util.time_util import convert_ms
import src.util.const as c
import os
import numpy

class ReplaceButton(QPushButton):

    def __init__(self, to_replace, plugin_manager):
        super(ReplaceButton, self).__init__(to_replace)
        self.to_replace = to_replace
        self.clicked.connect(self.replace)
        self.plugin_manager = plugin_manager

    def replace(self):
        self.plugin_manager.replace_selection(self.to_replace)

class DeepSpeechThread(QThread):

    def __init__(self, parent, meta_data, project_folder_path):
        super(DeepSpeechThread, self).__init__()
        self.parent = parent
        self.project_folder_path = project_folder_path
        self.meta_data = meta_data

    def run(self):
        self.model = self.get_model()

        media_file = file_util.get_file(self.project_folder_path, c.CON_COPY_POSTFIX)
        full = AudioSegment.from_file(media_file)

        for item in self.meta_data:
            current_word = item.get(c.WORD)
            org_start_time = item.get(c.START_TIME)
            start_time = max(org_start_time - 0.5, 0)
            clip = full[start_time * 1000:start_time * 1000 + 1000]
            buffer = clip.raw_data
            data = numpy.frombuffer(buffer, dtype=numpy.int16)
            result = self.model.sttWithMetadata(data, num_results=3)

            possible_words = []
            for candidate in result.transcripts:
                word = ""
                for t in candidate.tokens:
                    text = t.text
                    if text is not " ":
                        word += text
                    else:
                        if word not in possible_words and word != current_word:
                            possible_words.append(word)
                        word = ""
            self.parent.signal.done.emit({org_start_time: possible_words})

    def get_model(self):
        model_path = os.path.join(c.MODEL_PATH, self.parent.plugin_manager.get_language())
        files = [f for f in listdir(model_path) if isfile(join(model_path, f))]

        model_files = [s for s in files if ".pbmm" in s]

        if len(model_files) != 1:
            return None

        model = Model(os.path.join(model_path, model_files[0]))

        scorer_files = [s for s in files if ".scorer" in s]
        if len(scorer_files) == 1:
            model.enableExternalScorer(model_path + os.path.sep + scorer_files[0])

        return model

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.model = None
        self.thread = None
        self.lan = None
        self.alternatives = {}
        self.signal = DSSignal()
        self.signal.done.connect(self.add_alternatives)

    def project_loaded(self):
        meta_data = file_util.get_value_from_shelve(self.plugin_manager.get_project_folder_path(), c.TRANSCRIPTION_META_DATA)
        self.thread = DeepSpeechThread(self, meta_data, self.plugin_manager.get_project_folder_path())
        self.thread.start()

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        if len(word_meta_data) == 0:
            return

        for m_d in word_meta_data:
            forbidden_words = [word]
            siblings = list(filter(None, [self.plugin_manager.get_word_at(word_pos - 1),
                                          self.plugin_manager.get_word_at(word_pos + 1)]))
            forbidden_words += siblings
            forbidden_words = [w.lower() for w in forbidden_words]

            alternative_words = self.alternatives.get(m_d.get(c.START_TIME))
            if alternative_words is None:
                alternative_words = []

            btns = []
            for word in alternative_words:
                if word in forbidden_words:
                    continue
                btns.append(ReplaceButton(word, self.plugin_manager))
            self.plugin_manager.add_new_word_by_word_action(btns, (self.get_name() if len(btns) > 0 else "No alternatives") + " at " + convert_ms(m_d.get(c.START_TIME) * 1000), word, word_pos)

    def add_alternatives(self, alternatives):
        self.alternatives.update(alternatives)

    def get_name(self) -> str:
        return "DeepSpeech alternatives"

class DSSignal(QObject):
    done = Signal(dict)