import argparse
import os
import logging
from rich.logging import RichHandler
from rich.console import Console
from voice_cloner import VoiceCloner

# Configure logging with Rich for a better terminal experience
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("voice_cloner")

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Clone a voice and generate speech.")
    parser.add_argument("-i", "--input_voice", required=True, help="Path to the original voice WAV/MP3 file (REQUIRED).")
    parser.add_argument("-t", "--text", required=True, help="Text to be converted to speech (REQUIRED).")
    parser.add_argument("-o", "--output_file", required=True, help="Path and name of the output audio file (REQUIRED).")

    # Parse arguments with error handling
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2:  # Code 2 indicates missing or incorrect arguments
            parser.print_help()
            return

    # Ensure the directory for the output file exists
    output_dir = os.path.dirname(args.output_file)
    os.makedirs(output_dir, exist_ok=True)

    try:
        logger.info(f"[bold cyan] Initializing VoiceCloner with reference voice:[/bold cyan] {args.input_voice}")
        cloner = VoiceCloner(speaker_wav=args.input_voice)

        logger.info("[bold green] Generating speech...[/bold green]")
        cloner.say(args.text, play_audio=True, save_audio=True, output_file=args.output_file)

        logger.info(f"[bold green] Speech successfully generated and saved to:[/bold green] {args.output_file}")
    except FileNotFoundError:
        logger.error(f"[bold red] Error:[/bold red] Input voice file not found at {args.input_voice}")
    except Exception as e:
        logger.error(f"[bold red] An unexpected error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()