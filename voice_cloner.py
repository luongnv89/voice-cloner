import os
import torch
import io
import sounddevice as sd
import soundfile as sf
from TTS.api import TTS
from datetime import datetime

class VoiceCloner:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", speaker_wav="path_to_speaker_reference.wav", device=None):
        """
        Initialize the VoiceCloner class.

        Args:
            model_name (str): Name of the TTS model to use.
            speaker_wav (str): Path to the reference audio file for the speaker.
            device (str): Device to use for inference ('cuda' or 'cpu'). If None, it auto-detects.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.speaker_wav = speaker_wav
        self.model_name = model_name

        # Initialize the TTS model
        self.tts = TTS(model_name=self.model_name, progress_bar=False, gpu=(self.device == "cuda"))

        # Verify the speaker reference file exists
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(f"Speaker reference file not found: {self.speaker_wav}")

    def say(self, text_to_voice, language="en", play_audio=True, save_audio=False, speed=1.0):
        """
        Convert the input text to speech using the cloned voice and play it.

        Args:
            text_to_voice (str): Text to convert to speech.
            language (str): Language of the text (default is "en").
            play_audio (bool): Whether to play the audio after generation (default is True).
            save_audio (bool): Whether to save the audio to a file (default is False).
            speed (float): Playback speed multiplier (default is 1.0). Values > 1.0 make it faster.
        """
        # Generate speech directly to an in-memory buffer
        with io.BytesIO() as audio_buffer:
            self.tts.tts_to_file(
                text=text_to_voice,
                speaker_wav=self.speaker_wav,
                file_path=audio_buffer,
                language=language
            )
            audio_buffer.seek(0)
            audio_data, samplerate = self._load_audio_from_buffer(audio_buffer)

        # Save the audio to a file if save_audio is True
        if save_audio:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate timestamp
            save_path = f"audio_{timestamp}.wav"  # Create filename with timestamp
            self._save_audio_to_file(audio_data, samplerate, save_path)

        # Play the audio if requested
        if play_audio:
            self._play_audio(audio_data, samplerate, speed)

    def _load_audio_from_buffer(self, buffer):
        """
        Load audio data from an in-memory buffer.

        Args:
            buffer: In-memory buffer containing audio data.
        Returns:
            audio_data (numpy.ndarray): Audio data as a NumPy array.
            samplerate (int): Sample rate of the audio.
        """

        buffer.seek(0)
        audio_data, samplerate = sf.read(buffer)
        return audio_data, samplerate

    def _save_audio_to_file(self, audio_data, samplerate, save_path):
        """
        Save the audio data to a file.

        Args:
            audio_data (numpy.ndarray): Audio data as a NumPy array.
            samplerate (int): Sample rate of the audio.
            save_path (str): Path to save the audio file.
        """
        try:
            sf.write(save_path, audio_data, samplerate)
            print(f"Audio saved to {save_path}")
        except Exception as e:
            print(f"Error saving audio to file: {e}")

    def _play_audio(self, audio_data, samplerate, speed=1.0):
        """
        Play the audio data with adjustable speed.

        Args:
            audio_data (numpy.ndarray): Audio data as a NumPy array.
            samplerate (int): Sample rate of the audio.
            speed (float): Playback speed multiplier (default is 1.0). Values > 1.0 make it faster.
        """
        try:
            # Adjust the sample rate based on the speed
            adjusted_samplerate = int(samplerate * speed)
            sd.play(audio_data, adjusted_samplerate)
            sd.wait()  # Wait until the audio is finished playing
        except Exception as e:
            print(f"Error playing audio: {e}")
