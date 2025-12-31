from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class EngineControlsBase(QWidget):
    """Base class for engine-specific control widgets."""

    parameters_changed = Signal(dict)

    def get_parameters(self) -> dict[str, Any]:
        """Return current parameter values."""
        raise NotImplementedError


class CoquiControls(EngineControlsBase):
    """Control widget for Coqui XTTS v2 engine."""

    LANGUAGES = [
        ("English", "en"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de"),
        ("Italian", "it"),
        ("Portuguese", "pt"),
        ("Polish", "pl"),
        ("Turkish", "tr"),
        ("Russian", "ru"),
        ("Dutch", "nl"),
        ("Czech", "cs"),
        ("Arabic", "ar"),
        ("Chinese", "zh"),
        ("Japanese", "ja"),
        ("Hungarian", "hu"),
        ("Korean", "ko"),
    ]

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Language selector
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        for display_name, code in self.LANGUAGES:
            self.lang_combo.addItem(display_name, code)
        self.lang_combo.currentIndexChanged.connect(self._on_param_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        # Temperature slider
        temp_group = QGroupBox("Temperature")
        temp_layout = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(10, 100)  # 0.1 to 1.0
        self.temp_slider.setValue(70)
        self.temp_slider.valueChanged.connect(self._on_param_changed)
        self.temp_label = QLabel("0.70")
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/100:.2f}"))
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)

        self.setLayout(layout)

    def _on_param_changed(self):
        self.parameters_changed.emit(self.get_parameters())

    def get_parameters(self) -> dict[str, Any]:
        return {
            "language": self.lang_combo.currentData(),
            "temperature": self.temp_slider.value() / 100.0,
        }


class ChatterboxControls(EngineControlsBase):
    """Control widget for Chatterbox engine."""

    PARALINGUISTIC_TAGS = ["laugh", "chuckle", "cough", "sigh", "gasp", "yawn"]

    def __init__(self, variant: str = "turbo"):
        super().__init__()
        self.variant = variant
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # CFG Weight slider
        cfg_group = QGroupBox("CFG Weight (text adherence)")
        cfg_layout = QHBoxLayout()
        self.cfg_slider = QSlider(Qt.Horizontal)
        self.cfg_slider.setRange(0, 100)  # 0.0 to 1.0
        self.cfg_slider.setValue(50)
        self.cfg_slider.valueChanged.connect(self._on_param_changed)
        self.cfg_label = QLabel("0.50")
        self.cfg_slider.valueChanged.connect(lambda v: self.cfg_label.setText(f"{v/100:.2f}"))
        cfg_layout.addWidget(QLabel("Less"))
        cfg_layout.addWidget(self.cfg_slider)
        cfg_layout.addWidget(QLabel("More"))
        cfg_layout.addWidget(self.cfg_label)
        cfg_group.setLayout(cfg_layout)
        layout.addWidget(cfg_group)

        # Exaggeration slider
        exag_group = QGroupBox("Exaggeration (expressiveness)")
        exag_layout = QHBoxLayout()
        self.exag_slider = QSlider(Qt.Horizontal)
        self.exag_slider.setRange(0, 150)  # 0.0 to 1.5
        self.exag_slider.setValue(50)
        self.exag_slider.valueChanged.connect(self._on_param_changed)
        self.exag_label = QLabel("0.50")
        self.exag_slider.valueChanged.connect(lambda v: self.exag_label.setText(f"{v/100:.2f}"))
        exag_layout.addWidget(QLabel("Subtle"))
        exag_layout.addWidget(self.exag_slider)
        exag_layout.addWidget(QLabel("Dramatic"))
        exag_layout.addWidget(self.exag_label)
        exag_group.setLayout(exag_layout)
        layout.addWidget(exag_group)

        # Paralinguistic tags help (Turbo only)
        if self.variant == "turbo":
            tag_layout = QHBoxLayout()
            self.tag_button = QPushButton("Paralinguistic Tags Help")
            self.tag_button.clicked.connect(self._show_tags_help)
            tag_layout.addWidget(self.tag_button)
            tag_layout.addStretch()
            layout.addLayout(tag_layout)

        self.setLayout(layout)

    def _on_param_changed(self):
        self.parameters_changed.emit(self.get_parameters())

    def _show_tags_help(self):
        tags_text = ", ".join([f"[{tag}]" for tag in self.PARALINGUISTIC_TAGS])
        QMessageBox.information(
            self,
            "Paralinguistic Tags",
            f"Chatterbox Turbo supports these expressive tags:\n\n"
            f"{tags_text}\n\n"
            f"Example usage:\n"
            f"'That's hilarious [laugh]!'\n"
            f"'*sighs* [sigh] I can't believe this...'\n\n"
            f"Place tags where you want the sound to occur.",
        )

    def get_parameters(self) -> dict[str, Any]:
        return {
            "cfg_weight": self.cfg_slider.value() / 100.0,
            "exaggeration": self.exag_slider.value() / 100.0,
        }


class EngineControlsFactory:
    """Factory for creating engine-specific control widgets."""

    @staticmethod
    def create(engine_name: str) -> EngineControlsBase:
        """
        Create control widget for the specified engine.

        Args:
            engine_name: Engine identifier (e.g., "coqui", "chatterbox-turbo")

        Returns:
            EngineControlsBase widget instance
        """
        if engine_name == "coqui":
            return CoquiControls()
        elif engine_name == "chatterbox-turbo":
            return ChatterboxControls(variant="turbo")
        elif engine_name == "chatterbox-standard":
            return ChatterboxControls(variant="standard")
        else:
            # Return empty widget for unknown engines
            return EngineControlsBase()
