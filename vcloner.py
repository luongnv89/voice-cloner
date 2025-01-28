import argparse
from voice_cloner import VoiceCloner

def main():
    parser = argparse.ArgumentParser(description="Clone a voice and generate speech.")
    parser.add_argument("-i", "--input_voice", required=True, help="Path to the original voice WAV file (REQUIRED).")
    parser.add_argument("-t", "--text", required=True, help="Text to be converted to speech (REQUIRED).")

    # Add error handling for missing or incorrect arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:  # Catch the SystemExit exception raised by argparse
        if e.code == 2:  # Code 2 indicates an error (missing or incorrect arguments)
            parser.print_help()  # Print the help message
            return  # Exit the program

    try:
        cloner = VoiceCloner(speaker_wav=args.input_voice)
        cloner.say(args.text, play_audio=True, save_audio=True)
        print("Speech generated successfully")
    except FileNotFoundError:
        print(f"Error: Input voice file not found at {args.input_voice}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()