import os
import torch
import sounddevice as sd
import soundfile as sf
from TTS.api import TTS
from datetime import datetime
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.status import Status
import warnings
from transformers import logging as transformers_logging

# Suppress warnings globally
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Suppress specific warnings from Hugging Face Transformers
transformers_logging.set_verbosity_error()

# Set up logging with RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("voice_cloner")
console = Console()

class VoiceCloner:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", speaker_wav="path_to_speaker_reference.wav", device=None):
        """
        Initialize the VoiceCloner class.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.speaker_wav = speaker_wav
        self.model_name = model_name

        logger.info(f"Initializing VoiceCloner with model: {self.model_name}, device: {self.device}")

        # Initialize the TTS model only once
        self.tts = TTS(model_name=self.model_name, progress_bar=False, gpu=(self.device == "cuda"))
        logger.info("TTS model initialized successfully.")

        # Ensure the speaker reference file exists
        if not os.path.exists(self.speaker_wav):
            logger.error(f"Speaker reference file not found: {self.speaker_wav}")
            raise FileNotFoundError(f"Speaker reference file not found: {self.speaker_wav}")

        logger.info(f"Speaker reference file loaded: {self.speaker_wav}")

    def say(self, text_to_voice, language="en", play_audio=True, save_audio=False, output_file=None, speed=1.0):
        """
        Convert text to speech using the cloned voice.
        """
        logger.info(f"Generating speech for: '{text_to_voice}' [{language}]")

        # If saving audio, determine output file name
        if save_audio:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"generated_audio_{timestamp}.wav"

            output_dir = os.path.dirname(output_file) or "."
            os.makedirs(output_dir, exist_ok=True)

        with console.status("[bold cyan]Generating audio...[/bold cyan]") as status:
            try:
                if save_audio:
                    self.tts.tts_to_file(
                        text=text_to_voice,
                        speaker_wav=self.speaker_wav,
                        file_path=output_file,
                        language=language,
                        gpt_cond_len=128,
                        temperature=0.7,
                    )
                    logger.info(f"Audio saved to {output_file}")
                    audio_data, samplerate = sf.read(output_file)
                else:
                    temp_file = "temp_audio.wav"
                    self.tts.tts_to_file(
                        text=text_to_voice,
                        speaker_wav=self.speaker_wav,
                        file_path=temp_file,
                        language=language,
                        gpt_cond_len=128,
                        temperature=0.7,
                    )
                    audio_data, samplerate = sf.read(temp_file)
                    os.remove(temp_file)

                if play_audio:
                    self._play_audio(audio_data, samplerate, speed)

            except Exception as e:
                logger.error(f"Error during TTS generation: {e}")

    def _play_audio(self, audio_data, samplerate, speed=1.0):
        """
        Play the generated audio.
        """
        try:
            adjusted_samplerate = int(samplerate * speed)
            sd.play(audio_data, adjusted_samplerate)
            sd.wait()
            logger.info("Audio playback finished.")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")