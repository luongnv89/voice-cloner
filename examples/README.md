# Examples

This directory contains example scripts demonstrating VoiceCloner usage.

## Scripts

### basic_usage.py

Demonstrates basic voice cloning with Coqui XTTS v2:

```bash
python examples/basic_usage.py
```

Features:
- Initializing VoiceCloner with a speaker reference
- Converting text to speech
- Saving audio files

### chatterbox_demo.py

Demonstrates Chatterbox TTS with expressive speech:

```bash
python examples/chatterbox_demo.py
```

Features:
- Using Chatterbox Turbo engine
- Paralinguistic tags (`[sigh]`, `[laugh]`, etc.)
- Adjusting CFG weight and exaggeration

## Prerequisites

1. Install VoiceCloner:
   ```bash
   pip install -e .
   ```

2. For Chatterbox examples:
   ```bash
   pip install -e ".[chatterbox]"
   ```

3. Add voice samples to `voice-samples/` directory.

## Output

Generated audio files are saved to `output-examples/` directory.
