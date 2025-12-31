import logging

from tts_engine_base import TTSEngineBase

logger = logging.getLogger("voice_cloner.factory")


class TTSFactory:
    """Factory for creating TTS engine instances."""

    # Engine registry: name -> (engine_class, variant_kwargs)
    _registry: dict[str, tuple] = {}

    # Engine display names for UI
    _display_names: dict[str, str] = {}

    @classmethod
    def register(cls, name: str, engine_class: type[TTSEngineBase], display_name: str, **default_kwargs):
        """
        Register an engine class.

        Args:
            name: Unique identifier for the engine (e.g., "chatterbox-turbo")
            engine_class: The engine class to instantiate
            display_name: Human-readable name for UI
            **default_kwargs: Default kwargs passed to engine constructor
        """
        cls._registry[name] = (engine_class, default_kwargs)
        cls._display_names[name] = display_name
        logger.debug(f"Registered TTS engine: {name}")

    @classmethod
    def create(cls, engine_name: str, speaker_wav: str, device: str | None = None, **engine_kwargs) -> TTSEngineBase:
        """
        Create an engine instance.

        Args:
            engine_name: Registered engine name
            speaker_wav: Path to speaker reference audio
            device: Device to use ("cuda" or "cpu")
            **engine_kwargs: Additional engine-specific parameters

        Returns:
            Configured TTSEngineBase instance
        """
        if engine_name not in cls._registry:
            available = list(cls._registry.keys())
            raise ValueError(f"Unknown engine: '{engine_name}'. " f"Available engines: {available}")

        engine_class, default_kwargs = cls._registry[engine_name]

        # Merge default kwargs with provided kwargs
        merged_kwargs = {**default_kwargs, **engine_kwargs}

        logger.info(f"Creating TTS engine: {engine_name}")
        return engine_class(speaker_wav=speaker_wav, device=device, **merged_kwargs)

    @classmethod
    def available_engines(cls) -> list[str]:
        """Get list of registered engine names."""
        return list(cls._registry.keys())

    @classmethod
    def get_display_name(cls, engine_name: str) -> str:
        """Get human-readable display name for an engine."""
        return cls._display_names.get(engine_name, engine_name)

    @classmethod
    def get_engine_info(cls) -> dict[str, str]:
        """Get dict of engine_name -> display_name for all engines."""
        return cls._display_names.copy()

    @classmethod
    def is_available(cls, engine_name: str) -> bool:
        """Check if an engine's dependencies are installed."""
        if engine_name not in cls._registry:
            return False

        engine_class, _ = cls._registry[engine_name]

        # Check for required imports
        try:
            if "coqui" in engine_name.lower():
                import TTS  # noqa: F401
            elif "chatterbox" in engine_name.lower():
                import chatterbox  # noqa: F401
            return True
        except ImportError:
            return False


def _register_default_engines():
    """Register the default TTS engines."""
    # Register Coqui engine
    try:
        from engines.coqui_engine import CoquiEngine

        TTSFactory.register(name="coqui", engine_class=CoquiEngine, display_name="Coqui XTTS v2")
    except ImportError as e:
        logger.warning(f"Coqui engine not available: {e}")

    # Register Chatterbox engines
    try:
        from engines.chatterbox_engine import ChatterboxEngine

        # Chatterbox Turbo (fast, supports paralinguistic tags)
        TTSFactory.register(
            name="chatterbox-turbo",
            engine_class=ChatterboxEngine,
            display_name="Chatterbox Turbo (350M)",
            variant="turbo",
        )

        # Chatterbox Standard (higher quality)
        TTSFactory.register(
            name="chatterbox-standard",
            engine_class=ChatterboxEngine,
            display_name="Chatterbox Standard (500M)",
            variant="standard",
        )
    except ImportError as e:
        logger.warning(f"Chatterbox engines not available: {e}")


# Auto-register engines on module import
_register_default_engines()
