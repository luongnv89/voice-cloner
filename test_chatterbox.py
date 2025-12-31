#!/usr/bin/env python3
"""Test script for Chatterbox TTS engine."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_cloner import VoiceCloner

def main():
    # Use a voice sample
    voice_sample = "./voice-samples/geralt_original.mp3"
    output_file = "./output-examples/chatterbox_test.wav"

    print(f"Testing Chatterbox TTS with voice sample: {voice_sample}")
    print("-" * 50)

    # Create VoiceCloner with Chatterbox Turbo
    print("Initializing VoiceCloner with Chatterbox Turbo...")
    cloner = VoiceCloner.from_chatterbox(
        speaker_wav=voice_sample,
        variant="turbo"
    )

    # Generate speech
    text = "Hello, I am Geralt of Rivia. I hunt monsters for coin."
    print(f"Generating speech for: '{text}'")
    print("-" * 50)

    cloner.say(
        text,
        play_audio=False,  # Don't play, just save
        save_audio=True,
        output_file=output_file,
        cfg_weight=0.5,
        exaggeration=0.5
    )

    print(f"\nDone! Audio saved to: {output_file}")

    # Check file was created
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"File size: {size / 1024:.1f} KB")
    else:
        print("ERROR: Output file was not created!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
