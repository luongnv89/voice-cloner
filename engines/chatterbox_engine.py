import os
from typing import Tuple, Dict, Any, Optional, List, Literal
import numpy as np
import logging

from tts_engine_base import TTSEngineBase

logger = logging.getLogger("voice_cloner.chatterbox")

ChatterboxVariant = Literal["turbo", "standard"]


class ChatterboxEngine(TTSEngineBase):
    """TTS engine using Chatterbox by Resemble AI."""

    # Languages supported by multilingual features (when available)
    SUPPORTED_LANGUAGES = ["en"]  # Base Chatterbox is English-focused

    # Paralinguistic tags supported by Turbo variant
    PARALINGUISTIC_TAGS = ["laugh", "chuckle", "cough", "sigh", "gasp", "yawn"]

    def __init__(
        self,
        speaker_wav: str,
        device: Optional[str] = None,
        variant: ChatterboxVariant = "turbo"
    ):
        super().__init__(speaker_wav, device)
        self.variant = variant
        self._model = None  # Lazy loading
        self._sample_rate = None

    @property
    def model(self):
        """Lazy load model on first use."""
        if self._model is None:
            logger.info(f"Loading Chatterbox {self.variant} model...")
            try:
                from chatterbox.tts import ChatterboxTTS
                self._model = ChatterboxTTS.from_pretrained(device=self.device)
                self._sample_rate = self._model.sr
                logger.info(f"Chatterbox {self.variant} model loaded successfully")
            except ImportError as e:
                logger.error(
                    "chatterbox-tts package not installed. "
                    "Install with: pip install chatterbox-tts"
                )
                raise ImportError(
                    "chatterbox-tts package required. Install with: pip install chatterbox-tts"
                ) from e
        return self._model

    @property
    def sample_rate(self) -> int:
        """Get the model's sample rate."""
        if self._sample_rate is None:
            _ = self.model  # Trigger lazy load
        return self._sample_rate

    def generate(
        self,
        text: str,
        language: str = "en",
        cfg_weight: float = 0.5,
        exaggeration: float = 0.5,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """
        Generate audio using Chatterbox.

        Args:
            text: Text to synthesize. For Turbo, can include tags like [laugh].
            language: Language code (primarily "en" for base models).
            cfg_weight: CFG weight (0.0-1.0). Lower values = better pacing for fast speakers.
            exaggeration: Expressiveness (0.0-1.5). Higher = more dramatic.

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        # Validate reference audio exists
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(f"Speaker reference file not found: {self.speaker_wav}")

        # Generate audio
        wav_tensor = self.model.generate(
            text,
            audio_prompt_path=self.speaker_wav,
            cfg_weight=cfg_weight,
            exaggeration=exaggeration,
        )

        # Convert tensor to numpy array
        audio_data = wav_tensor.squeeze().cpu().numpy().astype(np.float32)

        return audio_data, self.sample_rate

    def get_supported_parameters(self) -> Dict[str, Dict[str, Any]]:
        params = {
            "cfg_weight": {
                "type": float,
                "default": 0.5,
                "description": "CFG weight - controls text adherence (0.0-1.0). Lower for fast speakers.",
                "min": 0.0,
                "max": 1.0
            },
            "exaggeration": {
                "type": float,
                "default": 0.5,
                "description": "Expressiveness level (0.0-1.5). Higher = more dramatic.",
                "min": 0.0,
                "max": 1.5
            }
        }
        return params

    @property
    def name(self) -> str:
        variant_names = {
            "turbo": "Chatterbox Turbo (350M)",
            "standard": "Chatterbox Standard (500M)"
        }
        return variant_names.get(self.variant, "Chatterbox")

    @property
    def supports_languages(self) -> List[str]:
        return self.SUPPORTED_LANGUAGES

    @property
    def supports_paralinguistic_tags(self) -> bool:
        """Check if this variant supports paralinguistic tags."""
        return self.variant == "turbo"

    def get_paralinguistic_tags(self) -> List[str]:
        """Get list of supported paralinguistic tags for Turbo variant."""
        if self.supports_paralinguistic_tags:
            return self.PARALINGUISTIC_TAGS
        return []

    def validate_text(self, text: str) -> Tuple[bool, str]:
        """
        Validate text for this engine variant.

        Returns:
            Tuple of (is_valid, message)
        """
        import re

        if not text.strip():
            return False, "Text cannot be empty"

        # Check for paralinguistic tags in non-Turbo variants
        tags_found = re.findall(r'\[(\w+)\]', text)
        if tags_found and not self.supports_paralinguistic_tags:
            return False, (
                f"Paralinguistic tags {tags_found} are only supported in Turbo variant. "
                "Switch to Chatterbox Turbo or remove the tags."
            )

        # Validate tags are recognized
        if tags_found and self.supports_paralinguistic_tags:
            invalid_tags = [t for t in tags_found if t not in self.PARALINGUISTIC_TAGS]
            if invalid_tags:
                return False, (
                    f"Unknown tags: {invalid_tags}. "
                    f"Supported: {self.PARALINGUISTIC_TAGS}"
                )

        return True, "OK"
