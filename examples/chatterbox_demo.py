#!/usr/bin/env python3
"""Demo script for Chatterbox TTS engine with paralinguistic tags."""

import os
import sys

# Add project root to path for running as standalone script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_cloner import VoiceCloner


def main():
    """Demonstrate Chatterbox TTS with expressive speech."""
    # Use a voice sample
    voice_sample = "./voice-samples/geralt_original.mp3"
    output_dir = "./output-examples"

    print(f"Testing Chatterbox TTS with voice sample: {voice_sample}")
    print("-" * 50)

    # Create VoiceCloner with Chatterbox Turbo
    print("Initializing VoiceCloner with Chatterbox Turbo...")
    cloner = VoiceCloner.from_chatterbox(speaker_wav=voice_sample, variant="turbo")

    # Example 1: Basic speech
    text1 = "Hello, I am Geralt of Rivia. I hunt monsters for coin."
    output1 = os.path.join(output_dir, "chatterbox_basic.wav")
    print(f"\nExample 1 - Basic: '{text1}'")

    cloner.say(
        text1,
        play_audio=False,
        save_audio=True,
        output_file=output1,
        cfg_weight=0.5,
        exaggeration=0.5,
    )
    print(f"Saved to: {output1}")

    # Example 2: With paralinguistic tags
    text2 = "That's a terrible idea [sigh]. But I suppose I have no choice."
    output2 = os.path.join(output_dir, "chatterbox_expressive.wav")
    print(f"\nExample 2 - Expressive: '{text2}'")

    cloner.say(
        text2,
        play_audio=False,
        save_audio=True,
        output_file=output2,
        cfg_weight=0.3,
        exaggeration=0.7,
    )
    print(f"Saved to: {output2}")

    print("\n" + "-" * 50)
    print("Done! Check output-examples/ for generated audio files.")

    # Verify files were created
    for output in [output1, output2]:
        if os.path.exists(output):
            size = os.path.getsize(output)
            print(f"  {os.path.basename(output)}: {size / 1024:.1f} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
