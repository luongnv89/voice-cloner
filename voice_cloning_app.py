import contextlib
import sys
import tempfile
import uuid
from pathlib import Path

import pygame
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.engine_controls import EngineControlsFactory
from voice_cloner import VoiceCloner


class CloneThread(QThread):
    """Thread for running TTS generation without blocking the UI."""

    finished = Signal(str, str)
    error_occurred = Signal(str)

    def __init__(self, text: str, voice_path: str, engine_name: str, engine_params: dict):
        super().__init__()
        self.text = text
        self.voice_path = voice_path
        self.engine_name = engine_name
        self.engine_params = engine_params
        self.output_path = None

    def run(self):
        try:
            # Create temporary output directory
            output_dir = Path(tempfile.gettempdir()) / "voice_cloning"
            output_dir.mkdir(exist_ok=True)

            # Generate unique filename
            self.output_path = output_dir / f"output_{uuid.uuid4().hex}.wav"

            # Create VoiceCloner with selected engine
            voice_cloner = VoiceCloner(speaker_wav=self.voice_path, engine=self.engine_name)

            # Generate audio
            voice_cloner.say(
                self.text, play_audio=False, save_audio=True, output_file=str(self.output_path), **self.engine_params
            )
            self.finished.emit(str(self.output_path), self.text)
        except Exception as e:
            self.error_occurred.emit(str(e))


class VoiceCloningApp(QMainWindow):
    """Main application window for Voice Cloner."""

    # Map display names to engine identifiers
    ENGINE_OPTIONS = [
        ("Coqui XTTS v2 (Multilingual)", "coqui"),
        ("Chatterbox Turbo (Fast)", "chatterbox-turbo"),
        ("Chatterbox Standard (High Quality)", "chatterbox-standard"),
    ]

    def __init__(self):
        super().__init__()
        self.current_audio = None
        self.voice_path = None
        self.engine_controls = None
        self.clone_thread = None
        self._temp_voice_file = None

        self.init_ui()
        self.setWindowTitle("VoiceCloner")
        self.setMinimumSize(650, 550)
        self.setWindowIcon(QIcon(str(Path(__file__).parent / "icon.jpg")))

        # Initialize pygame mixer for audio
        pygame.mixer.init()

    def closeEvent(self, event):
        """Clean up resources when window closes."""
        # Stop any playing audio
        pygame.mixer.music.stop()
        pygame.mixer.quit()

        # Wait for thread to finish
        if self.clone_thread and self.clone_thread.isRunning():
            self.clone_thread.quit()
            self.clone_thread.wait(1000)

        # Clean up temp files
        self._cleanup_temp_files()

        super().closeEvent(event)

    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        if self._temp_voice_file and Path(self._temp_voice_file).exists():
            with contextlib.suppress(OSError):
                Path(self._temp_voice_file).unlink()
        if self.current_audio and Path(self.current_audio).exists():
            with contextlib.suppress(OSError):
                Path(self.current_audio).unlink()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Model selection
        model_group = QGroupBox("TTS Engine")
        model_layout = QVBoxLayout()

        engine_row = QHBoxLayout()
        engine_row.addWidget(QLabel("Engine:"))
        self.engine_combo = QComboBox()
        for display_name, engine_id in self.ENGINE_OPTIONS:
            self.engine_combo.addItem(display_name, engine_id)
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        engine_row.addWidget(self.engine_combo)
        model_layout.addLayout(engine_row)

        # Container for engine-specific controls
        self.controls_container = QVBoxLayout()
        model_layout.addLayout(self.controls_container)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Initialize with first engine's controls
        self._update_engine_controls("coqui")

        # Text input
        text_group = QGroupBox("Text to Synthesize")
        text_layout = QVBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to generate audio...")
        self.text_input.setAcceptRichText(False)
        self.text_input.setMinimumHeight(100)
        text_layout.addWidget(self.text_input)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Voice file selection
        voice_group = QGroupBox("Voice Reference")
        voice_layout = QHBoxLayout()
        self.btn_select_voice = QPushButton("Select Voice File")
        self.btn_select_voice.clicked.connect(self.select_voice_file)
        self.voice_label = QLabel("No voice file selected")
        self.voice_label.setWordWrap(True)
        self.voice_label.setStyleSheet("color: #666;")
        voice_layout.addWidget(self.btn_select_voice)
        voice_layout.addWidget(self.voice_label, stretch=1)
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)

        # Generate button
        self.btn_generate = QPushButton("Generate Audio")
        self.btn_generate.clicked.connect(self.start_cloning)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #81C784;
            }
        """)
        layout.addWidget(self.btn_generate)

        # Result controls
        result_layout = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_audio)
        self.btn_play.hide()

        self.btn_save = QPushButton("Save Audio")
        self.btn_save.clicked.connect(self.save_audio)
        self.btn_save.hide()

        result_layout.addWidget(self.btn_play)
        result_layout.addWidget(self.btn_save)
        result_layout.addStretch()
        layout.addLayout(result_layout)

        layout.addStretch()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def _update_engine_controls(self, engine_name: str):
        """Update the engine-specific control widgets."""
        # Remove existing controls
        if self.engine_controls:
            self.controls_container.removeWidget(self.engine_controls)
            self.engine_controls.deleteLater()

        # Create new controls for selected engine
        self.engine_controls = EngineControlsFactory.create(engine_name)
        self.controls_container.addWidget(self.engine_controls)

    def on_engine_changed(self, index: int):
        """Handle engine selection change."""
        engine_name = self.engine_combo.currentData()
        self._update_engine_controls(engine_name)

    def select_voice_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Audio Files (*.wav *.mp3 *.ogg *.flac)")
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                self.voice_path = files[0]
                self.voice_label.setText(Path(self.voice_path).name)
                self.voice_label.setStyleSheet("color: #333;")

    def start_cloning(self):
        if not self.voice_path:
            QMessageBox.warning(
                self,
                "Missing Voice Reference",
                "Please select an audio file (.wav, .mp3, .ogg, .flac) as voice reference.",
            )
            return

        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Missing Text", "Please enter text to generate audio.")
            return

        # Check if a thread is already running
        if self.clone_thread and self.clone_thread.isRunning():
            QMessageBox.warning(self, "Generation In Progress", "Please wait for the current generation to complete.")
            return

        # Disable UI during processing
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generating audio...")
        self.btn_play.hide()
        self.btn_save.hide()
        self.btn_select_voice.setEnabled(False)
        self.engine_combo.setEnabled(False)

        # Get selected engine and parameters
        engine_name = self.engine_combo.currentData()
        engine_params = self.engine_controls.get_parameters()

        # Create temporary copy of voice file
        try:
            temp_voice = Path(tempfile.gettempdir()) / f"voice_{uuid.uuid4().hex}{Path(self.voice_path).suffix}"
            temp_voice.write_bytes(Path(self.voice_path).read_bytes())
            self._temp_voice_file = str(temp_voice)
        except (OSError, PermissionError, MemoryError) as e:
            self._reset_ui_state()
            QMessageBox.critical(self, "File Error", f"Cannot read voice file: {e}")
            return

        # Start cloning thread
        self.clone_thread = CloneThread(
            text=text, voice_path=str(temp_voice), engine_name=engine_name, engine_params=engine_params
        )
        self.clone_thread.finished.connect(self.on_cloning_finished)
        self.clone_thread.error_occurred.connect(self.on_cloning_error)
        self.clone_thread.start()

    def on_cloning_finished(self, output_path: str, text: str):
        self.current_audio = output_path
        self._reset_ui_state()
        self.btn_play.show()
        self.btn_save.show()

    @Slot(str)
    def on_cloning_error(self, message: str):
        self._reset_ui_state()
        QMessageBox.critical(self, "Generation Error", f"Failed to generate audio:\n\n{message}")

    def _reset_ui_state(self):
        """Reset UI to normal state after generation."""
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Generate Audio")
        self.btn_select_voice.setEnabled(True)
        self.engine_combo.setEnabled(True)

    def play_audio(self):
        if self.current_audio and Path(self.current_audio).exists():
            # Stop any currently playing audio first
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.play()

    def save_audio(self):
        if self.current_audio:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Audio File", f"cloned_voice_{uuid.uuid4().hex[:8]}.wav", "Wave Files (*.wav)"
            )
            if file_path:
                import shutil

                shutil.copy2(self.current_audio, file_path)
                QMessageBox.information(self, "Saved", f"Audio file saved to:\n{file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set modern style
    app.setStyle("Fusion")

    window = VoiceCloningApp()
    window.show()
    sys.exit(app.exec())
