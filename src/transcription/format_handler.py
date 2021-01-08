from moviepy import tools, editor


class FormatHandler():
    """Handels the format of the audio- and video-files"""

    def convert(self, file_path, wav_file_path, sample_rate):
        """Converts the file to a DeepSpeech suitable (wav) format.

        Args:
          file_path: Path of the file which should be converted.
          wav_file_path: Path of the converted wav.
          sample_rate: Sample rate.

        """

        type, extension = self.get_type_extension(file_path)
        if type == "video":
            clip = editor.VideoFileClip(file_path)
            clip.audio.write_audiofile(wav_file_path, ffmpeg_params=["-ac", "1", "-acodec", "pcm_s16le", "-ar", str(sample_rate)])
        if type == "audio":
            audio = editor.AudioFileClip(file_path)
            audio.write_audiofile(wav_file_path, ffmpeg_params=["-ac", "1", "-acodec", "pcm_s16le", "-ar", str(sample_rate)])


    def get_type_extension(self, file_path):
        """Returns the type (e.g. video or audio) and the extension of the file.

        Args:
          file_path: The file to check.

        Returns:
          Returns audio, video or none and the extension.
        """

        extension = file_path.split(".")[-1]
        dict_value = tools.extensions_dict.get(extension)
        if dict_value is not None:
            return dict_value.get("type"), extension
        return None, extension