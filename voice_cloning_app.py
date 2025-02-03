import sys
import os
import uuid
import tempfile
import subprocess
import pygame
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QTextEdit, QPushButton,
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QIcon
from voice_cloner import VoiceCloner  # Your updated cloner


class CloneThread(QThread):
    finished = Signal(str, str)
    error_occurred = Signal(str)

    def __init__(self, text, voice_path):
        super().__init__()
        self.text = text
        self.voice_path = voice_path
        self.output_path = None
        self.voice_cloner = VoiceCloner(speaker_wav=self.voice_path)

    def run(self):
        try:
            # Create temporary output directory
            output_dir = Path(tempfile.gettempdir()) / "voice_cloning"
            output_dir.mkdir(exist_ok=True)

            # Generate unique filename
            self.output_path = output_dir / f"output_{uuid.uuid4().hex}.wav"

            # Generate audio using the updated VoiceCloner
            self.voice_cloner.say(self.text, play_audio=False, save_audio=True, output_file=str(self.output_path))
            self.finished.emit(str(self.output_path), self.text)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # Clean up voice file if needed
            if Path(self.voice_path).exists():
                os.remove(self.voice_path)


class VoiceCloningApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_audio = None
        self.init_ui()
        self.setWindowTitle("VoiceCloner")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon(str(Path(__file__).parent / "icon.jpg")))

        # Initialize pygame mixer for audio
        pygame.mixer.init()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to generate audio...")
        self.text_input.setAcceptRichText(False)
        self.text_input.setMinimumHeight(100)
        layout.addWidget(QLabel("Input Text"))
        layout.addWidget(self.text_input)

        # Voice file selection
        self.voice_label = QLabel("No voice file selected")
        self.voice_label.setWordWrap(True)
        self.btn_select_voice = QPushButton("Select Original Voice")
        self.btn_select_voice.clicked.connect(self.select_voice_file)

        file_selector_layout = QHBoxLayout()
        file_selector_layout.addWidget(self.btn_select_voice)
        file_selector_layout.addWidget(self.voice_label)
        layout.addLayout(file_selector_layout)

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
        layout.addLayout(result_layout)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def select_voice_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Audio Files (*.wav *.mp3 *.ogg)")
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                self.voice_path = files[0]
                self.voice_label.setText(Path(self.voice_path).name)
                self.voice_label.setStyleSheet("color: #333;")

    def start_cloning(self):
        if not hasattr(self, 'voice_path'):
            QMessageBox.warning(self, "Missing Original Voice", "Please select an audio file (.wav, .m3, .ogg)")
            return

        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Missing Text", "Please enter text to generate audio")
            return
        # Disable UI during processing
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generating audio ...")
        self.btn_play.hide()
        self.btn_save.hide()
        # Disable the "Select Voice File" button
        self.btn_select_voice.setEnabled(False)

        # Create temporary copy of voice file
        temp_voice = Path(tempfile.gettempdir()) / f"voice_{uuid.uuid4().hex}{Path(self.voice_path).suffix}"
        temp_voice.write_bytes(Path(self.voice_path).read_bytes())

        # Start cloning thread
        self.clone_thread = CloneThread(text, str(temp_voice))
        self.clone_thread.finished.connect(self.on_cloning_finished)
        self.clone_thread.error_occurred.connect(self.on_cloning_error)
        self.clone_thread.start()

    def on_cloning_finished(self, output_path, text):
        self.current_audio = output_path
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Generate Audio")
        self.btn_play.show()
        self.btn_save.show()

        # Re-enable the "Select Voice File" button after cloning finishes
        self.btn_select_voice.setEnabled(True)

    @Slot(str)
    def on_cloning_error(self, message):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Generate Audio")
        QMessageBox.critical(self, "Error", f"Failed:\n{message}")

        # Re-enable the "Select Voice File" button after cloning error
        self.btn_select_voice.setEnabled(True)

    def play_audio(self):
        if self.current_audio and Path(self.current_audio).exists():
            pygame.mixer.music.load(self.current_audio)
            pygame.mixer.music.play()

    def save_audio(self):
        if self.current_audio:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Audio File",
                f"cloned_voice_{uuid.uuid4().hex[:8]}.wav",
                "Wave Files (*.wav)"
            )
            if file_path:
                Path(self.current_audio).rename(file_path)
                QMessageBox.information(self, "Saved", "Audio file saved successfully")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set modern style
    app.setStyle("Fusion")

    window = VoiceCloningApp()
    window.show()
    sys.exit(app.exec())