import os
import torch
import io
import sounddevice as sd
import soundfile as sf
from TTS.api import TTS
from datetime import datetime
import logging
from rich.logging import RichHandler
from rich.progress import Progress
import warnings
from transformers import logging as transformers_logging

# Suppress warnings globally
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)  # This also ignores the model loading warnings

# Suppress specific warnings from HuggingFace Transformers library
transformers_logging.set_verbosity_error()  # Only show errors, suppress warnings/info logs from HuggingFace

# Set up logging for your script with RichHandler
logging.basicConfig(
    level=logging.INFO,  # Adjust to INFO, DEBUG, etc., depending on the log level you want
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger()

# Suppress logs from third-party packages by using NullHandler
def disable_library_logs():
    loggers_to_disable = [
        'TTS',
        'sounddevice',
        'soundfile',
        'torch',  # Make sure to suppress logs from PyTorch as well
        'transformers',  # Suppress Hugging Face transformers library logs
    ]

    for logger_name in loggers_to_disable:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)  # Disables log messages by setting to critical level
        # Add NullHandler to completely ignore any logs
        if not logger.hasHandlers():
            logger.addHandler(logging.NullHandler())

disable_library_logs()

class VoiceCloner:
    def __init__(
        self,
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        speaker_wav="path_to_speaker_reference.wav",
        device=None,
    ):
        """
        Initialize the VoiceCloner class.
        Args:
            model_name (str): Name of the TTS model to use.
            speaker_wav (str): Path to the reference audio file for the speaker.
            device (str): Device to use for inference ('cuda' or 'cpu'). If None, it auto-detects.
        """
        self.device = (
            device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.speaker_wav = speaker_wav
        self.model_name = model_name
        logger.info(f"Initializing VoiceCloner with model: {self.model_name}, device: {self.device}")

        # Initialize the TTS model only once
        self.tts = TTS(
            model_name=self.model_name, progress_bar=False, gpu=(self.device == "cuda")
        )
        logger.info("TTS model initialized successfully.")

        # Verify the speaker reference file exists
        if not os.path.exists(self.speaker_wav):
            logger.error(f"Speaker reference file not found: {self.speaker_wav}")
            raise FileNotFoundError(f"Speaker reference file not found: {self.speaker_wav}")

        logger.info(f"Speaker reference file found: {self.speaker_wav}")
        # Extract the base name of the speaker reference file for use as a prefix
        self.prefix = os.path.splitext(os.path.basename(speaker_wav))[0]
        logger.info(f"Prefix set for saved audio: {self.prefix}")

    def say(
        self, text_to_voice, language="en", play_audio=True, save_audio=False, speed=1.0
    ):
        """
        Convert the input text to speech using the cloned voice and play it.
        Args:
            text_to_voice (str): Text to convert to speech.
            language (str): Language of the text (default is "en").
            play_audio (bool): Whether to play the audio after generation (default is True).
            save_audio (bool): Whether to save the audio to a file (default is False).
            speed (float): Playback speed multiplier (default is 1.0). Values > 1.0 make it faster.
        """
        logger.info(f"Starting speech generation for text: '{text_to_voice}' in language '{language}'")

        # Initialize the progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating audio...", total=100)

            # Generate speech directly to an in-memory buffer
            with io.BytesIO() as audio_buffer:
                logger.info("Generating audio from text...")
                self.tts.tts_to_file(
                    text=text_to_voice,
                    speaker_wav=self.speaker_wav,
                    file_path=audio_buffer,
                    language=language,
                    gpt_cond_len=128,
                    temperature=0.7,
                )
                # Update progress bar
                progress.update(task, advance=50)

                logger.info("Audio generation complete.")
                audio_buffer.seek(0)
                audio_data, samplerate = sf.read(audio_buffer)

                logger.info(f"Audio data loaded. Sample rate: {samplerate}, Audio length: {len(audio_data)} samples")

                # Update progress bar after audio loading
                progress.update(task, advance=30)

        # Save the audio data to a file if requested
        if save_audio:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate timestamp
            save_path = f"{self.prefix}_audio_{timestamp}.wav"  # Create filename with prefix and timestamp
            logger.info(f"Saving audio to {save_path}")
            self._save_audio_to_file(audio_data, samplerate, save_path)

        # Play the audio if requested
        if play_audio:
            logger.info(f"Playing audio with speed factor {speed}")
            self._play_audio(audio_data, samplerate, speed)

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
            logger.info(f"Audio successfully saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")

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
            logger.info(f"Adjusted sample rate: {adjusted_samplerate}")
            sd.play(audio_data, adjusted_samplerate)
            sd.wait()  # Wait until the audio is finished playing
            logger.info("Audio playback finished.")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")