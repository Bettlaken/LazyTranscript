from typing import List
from PySide2.QtCore import QThread, QObject, Signal
from PySide2.QtWidgets import QPushButton
from src.util import file_util
from src.util.plugin_abstract import IPlugin
from vosk import Model, KaldiRecognizer, SetLogLevel
from bisect import bisect
from src.util.time_util import convert_ms
import src.util.const as c
import json
import os
import wave

class ReplaceButton(QPushButton):

    def __init__(self, to_replace, plugin_manager):
        super(ReplaceButton, self).__init__(to_replace)
        self.to_replace = to_replace
        self.clicked.connect(self.replace)
        self.plugin_manager = plugin_manager

    def replace(self):
        self.plugin_manager.replace_selection(self.to_replace)

class VoskThread(QThread):

    def __init__(self, parent, meta_data, project_folder_path):
        super(VoskThread, self).__init__()
        self.parent = parent
        self.project_folder_path = project_folder_path
        self.meta_data = meta_data

    def run(self):
        result = {}
        media_file = file_util.get_file(self.project_folder_path, c.CON_COPY_POSTFIX)
        wf = wave.open(media_file)
        self.rec = self.get_recognizer(wf.getframerate())


        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                for r in json.loads(self.rec.Result())["result"]:
                    result[r["start"]] = r["word"]

        for r in json.loads(self.rec.FinalResult())["result"]:
            result[r["start"]] = r["word"]

        self.parent.signal.done.emit(result)

    def get_recognizer(self, framerate):
        SetLogLevel(-1)
        model = Model(os.path.join(c.PLUGIN_PATH, "vosk_alternatives", "model"))
        rec = KaldiRecognizer(model, framerate)
        return rec

class Plugin(IPlugin):

    def __init__(self, plugin_manager):
        super(Plugin, self).__init__(plugin_manager)
        self.model = None
        self.thread = None
        self.lan = None
        self.alternatives = {}
        self.signal = DSSignal()
        self.signal.done.connect(self.set_alternatives)

    def project_loaded(self):
        meta_data = file_util.get_value_from_shelve(self.plugin_manager.get_project_folder_path(), c.TRANSCRIPTION_META_DATA)
        self.thread = VoskThread(self, meta_data, self.plugin_manager.get_project_folder_path())
        self.thread.start()

    def get_word_action(self, word: str, word_meta_data: List[dict], word_pos: int):
        if len(word_meta_data) == 0 or len(self.alternatives) == 0:
            return

        keys = list(self.alternatives.keys())

        for m_d in word_meta_data:
            pos = bisect(keys, m_d.get(c.START_TIME))

            btns = []
            words = []
            if pos+1 < len(keys)-1:
                words.append(self.alternatives.get(keys[pos+1]))
            if pos-1 >= 0:
                words.append(self.alternatives.get(keys[pos-1]))
            if pos < len(keys) and pos > 0:
                words.append(self.alternatives.get(keys[pos]))

            forbidden_words = [word]
            siblings = list(filter(None, [self.plugin_manager.get_word_at(word_pos-1), self.plugin_manager.get_word_at(word_pos+1)]))
            forbidden_words += siblings
            forbidden_words = [w.lower() for w in forbidden_words]

            for w in words:
                if w in forbidden_words:
                    continue
                btns.append(ReplaceButton(w, self.plugin_manager))
            self.plugin_manager.add_new_word_by_word_action(btns, (self.get_name() if len(btns) > 0 else "No alternatives") + " at " + convert_ms(m_d.get(c.START_TIME) * 1000), word, word_pos)

    def set_alternatives(self, alternatives):
        print(alternatives)
        self.alternatives = alternatives

    def get_name(self) -> str:
        return "Vosk alternatives"

class DSSignal(QObject):
    done = Signal(dict)