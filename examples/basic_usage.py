#!/usr/bin/env python3
"""Basic usage example for VoiceCloner with Coqui TTS."""

import os
import sys

# Add project root to path for running as standalone script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_cloner import VoiceCloner


def main():
    """Demonstrate basic VoiceCloner usage."""
    # Initialize VoiceCloner with a speaker reference
    speaker_wav = "./voice-samples/jack-sparrow_original.mp3"

    print(f"Initializing VoiceCloner with: {speaker_wav}")
    cloner = VoiceCloner(speaker_wav=speaker_wav)

    # Example texts to convert
    texts = [
        "Hello! This is a demonstration of the VoiceCloner library.",
        "VoiceCloner can clone any voice from a short audio sample.",
    ]

    for i, text in enumerate(texts):
        print(f"\nGenerating speech {i + 1}: '{text[:50]}...'")
        cloner.say(
            text,
            language="en",
            play_audio=True,
            save_audio=True,
            output_file=f"./output-examples/basic_demo_{i + 1}.wav",
        )

    print("\nDone! Check output-examples/ for generated audio files.")


if __name__ == "__main__":
    main()
