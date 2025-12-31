from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
import numpy as np
import torch


class TTSEngineBase(ABC):
    """Abstract base class for TTS engines."""

    def __init__(self, speaker_wav: str, device: Optional[str] = None):
        self.speaker_wav = speaker_wav
        self.device = device or self._default_device()

    @abstractmethod
    def generate(
        self,
        text: str,
        language: str = "en",
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """
        Generate audio from text.

        Args:
            text: The text to convert to speech.
            language: Language code (e.g., "en", "fr", "de").
            **kwargs: Engine-specific parameters.

        Returns:
            Tuple of (audio_data: np.ndarray, sample_rate: int)
        """
        pass

    @abstractmethod
    def get_supported_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Return supported parameters with their metadata.

        Returns:
            Dict mapping param_name -> {"type": type, "default": value, "description": str}
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable engine name."""
        pass

    @property
    @abstractmethod
    def supports_languages(self) -> list:
        """List of supported language codes."""
        pass

    @staticmethod
    def _default_device() -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"
