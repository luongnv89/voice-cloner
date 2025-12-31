import logging
import os
import tempfile
from typing import Any

import numpy as np
import soundfile as sf

from tts_engine_base import TTSEngineBase

logger = logging.getLogger("voice_cloner.coqui")


def _ensure_mono(audio_data: np.ndarray) -> np.ndarray:
    """Ensure audio is mono (1D array)."""
    if len(audio_data.shape) > 1:
        return audio_data.mean(axis=1)
    return audio_data


class CoquiEngine(TTSEngineBase):
    """TTS engine using Coqui TTS (XTTS v2)."""

    SUPPORTED_LANGUAGES = [
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "pl",
        "tr",
        "ru",
        "nl",
        "cs",
        "ar",
        "zh",
        "ja",
        "hu",
        "ko",
    ]

    def __init__(
        self,
        speaker_wav: str,
        device: str | None = None,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
    ):
        super().__init__(speaker_wav, device)
        self.model_name = model_name
        self._tts = None  # Lazy loading

    @property
    def tts(self):
        """Lazy load TTS model on first use."""
        if self._tts is None:
            from TTS.api import TTS

            logger.info(f"Loading Coqui TTS model: {self.model_name}")
            self._tts = TTS(model_name=self.model_name, progress_bar=False, gpu=(self.device == "cuda"))
            logger.info("Coqui TTS model loaded successfully")
        return self._tts

    def generate(
        self, text: str, language: str = "en", temperature: float = 0.7, gpt_cond_len: int = 128, **kwargs
    ) -> tuple[np.ndarray, int]:
        """
        Generate audio using Coqui TTS.

        Args:
            text: Text to synthesize.
            language: Language code.
            temperature: Sampling temperature (0.1-1.0).
            gpt_cond_len: GPT conditioning length.

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        # Create temp file for output using mkstemp for better cross-platform support
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)  # Close file descriptor immediately

        try:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.speaker_wav,
                file_path=temp_path,
                language=language,
                gpt_cond_len=gpt_cond_len,
                temperature=temperature,
            )
            audio_data, sample_rate = sf.read(temp_path)
            audio_data = _ensure_mono(audio_data)
            return audio_data.astype(np.float32), sample_rate
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_supported_parameters(self) -> dict[str, dict[str, Any]]:
        return {
            "language": {
                "type": str,
                "default": "en",
                "description": "Language code (en, es, fr, de, etc.)",
                "options": self.SUPPORTED_LANGUAGES,
            },
            "temperature": {
                "type": float,
                "default": 0.7,
                "description": "Sampling temperature (0.1-1.0)",
                "min": 0.1,
                "max": 1.0,
            },
            "gpt_cond_len": {
                "type": int,
                "default": 128,
                "description": "GPT conditioning length",
                "min": 32,
                "max": 256,
            },
        }

    @property
    def name(self) -> str:
        return "Coqui XTTS v2"

    @property
    def supports_languages(self) -> list[str]:
        return self.SUPPORTED_LANGUAGES
