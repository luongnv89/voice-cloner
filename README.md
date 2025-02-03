# VoiceCloner: Text-to-Speech with Voice Cloning

VoiceCloner is a Python library that uses the Coqui TTS library to clone a specific voice and generate speech in that voice. It supports multilingual text-to-speech, customizable playback speed, and saving audio files with timestamped filenames.  It also includes command-line interface (CLI) tools for easy usage.

---

## Features
- **Voice Cloning**: Clone a specific voice from a reference audio file.
- **Text-to-Speech**: Convert text into speech using the cloned voice.
- **Multilingual Support**: Supports multiple languages (e.g., English, Spanish, etc.).
- **Customizable Playback Speed**: Adjust the playback speed of the generated audio.
- **Save Audio Files**: Save generated audio files with timestamped filenames.
- **Low Latency Playback**: Play audio directly with minimal delay.
- **Command-Line Interface (CLI)**:  Easily use the voice cloner from the command line.

---

## Installation and Setup

### Prerequisites
1. **Python <=3.10**: Ensure Python is installed on your system.  (Python 3.10 or lower is recommended due to compatibility with the TTS library.)
2. **CUDA (Optional)**: For GPU acceleration, install CUDA and compatible drivers if you have an NVIDIA GPU.

### Step 1: Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/luongnv89/voice-cloner.git
cd voice-cloner
```

### Step 2: Set Up a Virtual Environment (Recommended)
Create and activate a virtual environment to manage dependencies:
```bash
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
Install the required Python packages:
```bash
pip install torch torchaudio TTS sounddevice soundfile
```

- **`torch`**: PyTorch for deep learning.
- **`torchaudio`**:  Audio processing library for PyTorch.
- **`TTS`**: Coqui TTS library for text-to-speech.
- **`sounddevice`**: For playing audio.
- **`soundfile`**: For reading/writing audio files.

### Step 4: Download the Speaker Reference File
Place your speaker reference audio file (e.g., `speaker.wav`) in the `voice-samples` directory or specify its path when initializing the `VoiceCloner` class.  A sample Barack Obama voice file is provided.

---

## Usage

### `VoiceCloner` application with simple GUI
To use the `VoiceCloner` application with interface

```bash
python voice_cloning_app.py
```
![VoiceCloner](./voice-cloner-app.png)

### Using the `VoiceCloner` Class (Programmatically)

#### 1. Initialize the `VoiceCloner` Class
To use the `VoiceCloner` class, import it and initialize it with the path to your speaker reference file:
```python
from voice_cloner import VoiceCloner

# Initialize the VoiceCloner class
speaker_wav = "./voice-samples/barack-obama_cloned.mp3"  # Replace with your speaker file path
cloner = VoiceCloner(speaker_wav=speaker_wav)

# Convert text to speech and play it
message = "Hello, this is a test of the text-to-speech system."
cloner.say(message)
```

- **`language`**: Specify the language of the text (e.g., `"en"` for English).
- **`play_audio`**: Set to `True` to play the audio after generation.
- **`save_audio`**: Set to `True` to save the audio file with a timestamped filename.
- **`speed`**: Adjust the playback speed (e.g., `1.5` for 1.5x speed).


#### 3. Save Audio to a File
If `save_audio=True`, the audio file will be saved with a timestamped filename (e.g., `audio_YYYYMMDD_HHMMSS.wav`).


### Using the CLI Tool (`vcloner.py`)

The `vcloner.py` script provides a command-line interface for easier usage:

```bash
python vcloner.py -i path/to/input_voice.wav -t "Your text here"
```

- `-i` or `--input_voice`: Path to your input voice WAV file (REQUIRED).
- `-t` or `--text`: Text to be converted to speech (REQUIRED).

**Example:**

```bash
python vcloner.py -i ./voice-samples/barack-obama_cloned.mp3 -t "This is a test"
```

This will generate a WAV file containing the specified text spoken in the cloned voice.

---

### Example Script (`main.py`)

The `main.py` file demonstrates how to use the `VoiceCloner` class to process multiple transcripts:

```python
from voice_cloner import VoiceCloner

# ... (code as shown in the original main.py file)
```


---

## Integrating `VoiceCloner` into Other Applications

To use the `VoiceCloner` class in other applications, follow these steps:

1. **Copy the `VoiceCloner` Class**:
   - Copy the `voice_cloner.py` file into your project directory.

2. **Install Dependencies**:
   - Ensure all dependencies (`torch`, `TTS`, `sounddevice`, `soundfile`) are installed in your environment.

3. **Import and Use**:
   - Import the `VoiceCloner` class and use it as shown in the example above.

Example:
```python
from voice_cloner import VoiceCloner

# Initialize and use VoiceCloner
speaker_wav = "path/to/speaker_reference.wav"
cloner = VoiceCloner(speaker_wav=speaker_wav)

# Convert text to speech
cloner.say("Welcome to my application!", language="en", play_audio=True)
```

---

## Troubleshooting

### 1. **CUDA Not Available**
If you encounter an error related to CUDA, ensure that:
- You have installed the correct version of PyTorch with CUDA support.
- Your GPU drivers are up to date.

### 2. **Audio Playback Issues**
If audio playback doesn’t work:
- Ensure `sounddevice` is installed correctly.
- Check your system’s audio output settings.

### 3. **File Not Found Error**
If the speaker reference file is not found:
- Double-check the file path provided to the `VoiceCloner` class.
- Make sure the file exists and the path is correct.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
- [Coqui TTS](https://github.com/coqui-ai/TTS): The text-to-speech library used in this project.
- [PyTorch](https://pytorch.org/): For deep learning support.
- [SoundDevice](https://python-sounddevice.readthedocs.io/): For audio playback.
- [VoicAI](https://aiartes.com/voiceai): for download voice sample of some famous people