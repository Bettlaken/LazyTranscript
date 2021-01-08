import os
import shutil
import src.util.const as c
from PySide2.QtCore import QThread, Signal, QObject
from src.transcription.deepspeech_transcriber import DeepSpeechTranscriber
from src.transcription.format_handler import FormatHandler
from src.util.file_util import save_to_shelve, write_text_file

class ProgressSignal(QObject):
    """Simple class to hold the Signals.

    The progress-signal is used to display the progress in the main-thread.
    The done-signal is used to notify the main-thread that the work is done.

    """
    progress = Signal(int)
    done = Signal(str)

class CreateThread(QThread):
    """This thread create a new project.

    Here the first transcription is started and the files are copied into the project directory.

    """
    def __init__(self, file_path, folder_path, project_name, language):
        QThread.__init__(self, None)
        self.signal = ProgressSignal()

        self.file_path = file_path
        self.folder_path = folder_path
        self.project_name = project_name
        self.language = language

    def run(self):
        """Method that is executed in the background.

        Here the create_project process is executed.

        """
        self.create_project(self.file_path, self.folder_path, self.project_name, self.language)
        self.signal.progress.emit(0)

    def create_project(self, file_path, folder_path, project_name, language):
        """Creates the Project.

        In order to do this:
            1. The project-folder will be created.
            2. The source-material will be copied and converted
            3. The converted version will be transcribed.
            4. The results will be saved.

        Args:
          file_path: The path of the source material.
          folder_path: The folder in which the project folder should be created.
          project_name: The project-name.
          language: The project language, e.g. en, de or other language tags.

        """
        type, extension = FormatHandler().get_type_extension(file_path)
        if type is None or type not in ["video", "audio"]:
            self.signal.done.emit(None)

        try:
            project_folder_path = os.path.join(folder_path, project_name)
            os.mkdir(project_folder_path)
            self.signal.progress.emit(20)
            new_file_name = os.path.basename(file_path).replace(".", c.ORIGNAL_POSTFIX)
            new_file_path = os.path.join(project_folder_path, new_file_name)
            shutil.copyfile(file_path, new_file_path)
            self.signal.progress.emit(40)
            save_to_shelve(project_folder_path, c.LANGUAGE, language)
            self.signal.progress.emit(60)
            text, transcription_list = DeepSpeechTranscriber().transcribe(new_file_path, language)
            self.signal.progress.emit(80)
            write_text_file(project_folder_path, text, c.TRANSCRIPTION)
            save_to_shelve(project_folder_path, c.TRANSCRIPTION_META_DATA, transcription_list)
            self.signal.progress.emit(100)
        except OSError:
            self.signal.done.emit(None)

        self.signal.done.emit(project_folder_path)