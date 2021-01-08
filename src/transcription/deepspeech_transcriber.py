import os
from os import listdir
from os.path import isfile, join
import numpy as np
from deepspeech import Model
import collections
import contextlib
import wave
import webrtcvad
import src.util.const as c
from pydub import AudioSegment
from src.transcription.format_handler import FormatHandler
from definitions import ROOT_DIR

class DeepSpeechTranscriber():
    """Creates the Transcription via DeepSpeech.

    Based on: https://github.com/mozilla/DeepSpeech-examples/tree/r0.8/vad_transcriber

    """

    def transcribe(self, file_path, language, aggressiveness = 3):
        """Creates the segments and transcribes the given file.

        Args:
          file_path: Path of the file which should be transcribed.
          language: Language in which the file should be transcribed.
          aggressiveness: Voice-activation aggressiveness. (Default value = 3)

        Returns:
          the transcription and the meta_data
        """

        format_handler = FormatHandler()
        type, extension = format_handler.get_type_extension(file_path)
        if type is None:
            return ""

        self.model = self.get_model(language)
        if self.model is None:
            return ""

        wav_file_path = file_path.replace(c.ORIGNAL_POSTFIX + extension, c.CON_COPY_POSTFIX + "wav")
        format_handler.convert(file_path, wav_file_path, self.model.sampleRate())

        audio, sample_rate = self.read_wave(wav_file_path)
        vad = webrtcvad.Vad(int(aggressiveness))
        frames = list(self.frame_generator(30, audio, sample_rate))
        segments = self.vad_collector(sample_rate, 30, 300, vad, frames)

        return self.stt(segments, wav_file_path)

    def stt(self, segments, file_path):
        """Execute the transcription for each segment.

        Args:
          segments: List of segments from the audio
          file_path: Path of the file which should be transcribed.

        Returns:
          The transcription iteself and the meta_data which contain the timestamps for the words.
        """

        output_string = ""
        token_meta_data_list = []

        sound = AudioSegment.from_file(file_path)
        sound_byte = sound.raw_data

        for i, segment in enumerate(segments):
            audio_before_byte = sound_byte[0:sound_byte.find(segment)]
            audio_before = AudioSegment(data=audio_before_byte, sample_width=2, frame_rate=16000, channels=1)

            audio = np.frombuffer(segment, dtype=np.int16)
            output_string = output_string + " " + self.model.stt(audio)
            meta_data = self.model.sttWithMetadata(audio)
            transcripts = meta_data.transcripts[0].tokens
            token_meta_data_list = token_meta_data_list + self.get_meta_data_result(transcripts, audio_before.duration_seconds)

        return output_string.strip(), token_meta_data_list

    def get_meta_data_result(self, transcripts, segment_start_time):
        """Sets the correct start_time and end_time for the words in the transcripts.

        Args:
          transcripts: List of recognized characters in this segment.
          segment_start_time:  Start time of the segment.

        Returns:
          The word dict with the start and end time.
        """

        result = []
        current_word = ""

        start_time_stamp = None
        for i in range(len(transcripts)):
            character = transcripts[i].text
            if character != " ":
                current_word = current_word + character
                if start_time_stamp is None:
                    start_time_stamp = transcripts[i].start_time
            if character == " " or i == (len(transcripts) - 1):
                temp = {}
                temp[c.START_TIME] = segment_start_time + start_time_stamp
                temp[c.END_TIME] = segment_start_time + transcripts[i].start_time
                temp[c.WORD] = current_word
                result.append(temp)
                current_word = ""
                start_time_stamp = None

        return result

    def read_wave(self, path):
        """Reads a .wav file.

        Args:
          path: path of the file.

        Returns:
          pcm audio data and sample rate
        """

        with contextlib.closing(wave.open(path, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000)
            frames = wf.getnframes()
            pcm_data = wf.readframes(frames)
            return pcm_data, sample_rate

    def frame_generator(self, frame_duration_ms, audio, sample_rate):
        """Generates audio frames from PCM audio data.

        Args:
          frame_duration_ms: Desired frame duration in miliseconds.
          audio: The audio itself.
          sample_rate: The sample rate of the audio

        Returns:
          Yields Frames of the requested duration.
        """

        n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
        offset = 0
        timestamp = 0.0
        duration = (float(n) / sample_rate) / 2.0
        while offset + n < len(audio):
            yield Frame(audio[offset:offset + n], timestamp, duration)
            timestamp += duration
            offset += n

    def vad_collector(self, sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
        """Filters out non-voiced audio frames.

        Given a webrtcvad.Vad and a source of audio frames, yields only
        the voiced audio.
        Uses a padded, sliding window algorithm over the audio frames.
        When more than 90% of the frames in the window are voiced (as
        reported by the VAD), the collector triggers and begins yielding
        audio frames. Then the collector waits until 90% of the frames in
        the window are unvoiced to detrigger.

        The window is padded at the front and back to provide a small
        amount of silence or the beginnings/endings of speech around the
        voiced frames.


        Args:
          sample_rate: The audio sample rate, in Hz.
          frame_duration_ms: The frame duration in milliseconds.
          padding_duration_ms: The amount to pad the window, in milliseconds.
          vad: An instance of webrtcvad.Vad.
          frames: a source of audio frames (sequence or generator).

        Returns:
          A generator that yields PCM audio data.
        """

        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        # We use a deque for our sliding window/ring buffer.
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
        # NOTTRIGGERED state.
        triggered = False

        voiced_frames = []
        for frame in frames:
            is_speech = vad.is_speech(frame.bytes, sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # If we're NOTTRIGGERED and more than 90% of the frames in
                # the ring buffer are voiced frames, then enter the
                # TRIGGERED state.
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    # We want to yield all the audio we see from now until
                    # we are NOTTRIGGERED, but we have to start with the
                    # audio that's already in the ring buffer.
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                # We're in the TRIGGERED state, so collect the audio data
                # and add it to the ring buffer.
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                # If more than 90% of the frames in the ring buffer are
                # unvoiced, then enter NOTTRIGGERED and yield whatever
                # audio we've collected.
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    yield b''.join([f.bytes for f in voiced_frames])
                    ring_buffer.clear()
                    voiced_frames = []

        if triggered:
            pass
        # If we have any leftover voiced audio when we run out of input,
        # yield it.
        if voiced_frames:
            yield b''.join([f.bytes for f in voiced_frames])

    def get_model(self, language):
        """Returns the DeepSpeech model.

        Args:
          language: Language-Tag which should exists as folder in the models folder.

        Returns:
          The DeepSpeech-Model.
        """

        model_path = os.path.join(ROOT_DIR, "models", language)
        files = [f for f in listdir(model_path) if isfile(join(model_path, f))]

        model_files = [s for s in files if ".pbmm" in s]

        if len(model_files) != 1:
            return None

        model = Model(os.path.join(model_path,model_files[0]))

        scorer_files = [s for s in files if ".scorer" in s]
        if len(scorer_files) == 1:
            model.enableExternalScorer(model_path + os.path.sep + scorer_files[0])

        return model

class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration
