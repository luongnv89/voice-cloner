import argparse
import logging
import os

from rich.console import Console
from rich.logging import RichHandler

from tts_factory import TTSFactory
from voice_cloner import VoiceCloner

# Configure logging with Rich for a better terminal experience
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger("voice_cloner")

console = Console()


def main():
    # Get available engines for help text
    available_engines = TTSFactory.available_engines()
    engines_help = ", ".join(available_engines)

    parser = argparse.ArgumentParser(
        description="Clone a voice and generate speech using multiple TTS engines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using Coqui (default)
  python vcloner.py -i voice.wav -t "Hello world" -o output.wav

  # Using Chatterbox Turbo (fast)
  python vcloner.py -i voice.wav -t "Hello world" -o output.wav --engine chatterbox-turbo

  # Using Chatterbox with custom parameters
  python vcloner.py -i voice.wav -t "That's funny [laugh]!" -o output.wav \\
      --engine chatterbox-turbo --cfg-weight 0.3 --exaggeration 0.7

  # List available engines
  python vcloner.py --list-engines
        """,
    )

    parser.add_argument(
        "-i", "--input_voice", help="Path to the original voice WAV/MP3 file (REQUIRED for generation)."
    )
    parser.add_argument("-t", "--text", help="Text to be converted to speech (REQUIRED for generation).")
    parser.add_argument("-o", "--output_file", help="Path and name of the output audio file (REQUIRED for generation).")
    parser.add_argument(
        "-e",
        "--engine",
        default="coqui",
        choices=available_engines,
        help=f"TTS engine to use. Available: {engines_help}. Default: coqui",
    )
    parser.add_argument(
        "-l", "--language", default="en", help="Language code (default: en). For Coqui: en, es, fr, de, etc."
    )

    # Coqui-specific arguments
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Coqui: Sampling temperature (0.1-1.0). Default: 0.7"
    )

    # Chatterbox-specific arguments
    parser.add_argument(
        "--cfg-weight",
        type=float,
        default=0.5,
        help="Chatterbox: CFG weight for text adherence (0.0-1.0). Lower for fast speakers. Default: 0.5",
    )
    parser.add_argument(
        "--exaggeration",
        type=float,
        default=0.5,
        help="Chatterbox: Expressiveness level (0.0-1.5). Higher = more dramatic. Default: 0.5",
    )

    # Utility arguments
    parser.add_argument("--list-engines", action="store_true", help="List available TTS engines and exit.")
    parser.add_argument("--no-play", action="store_true", help="Don't play audio after generation.")

    args = parser.parse_args()

    # Handle --list-engines
    if args.list_engines:
        console.print("\n[bold]Available TTS Engines:[/bold]\n")
        engine_info = TTSFactory.get_engine_info()
        for engine_id, display_name in engine_info.items():
            available = TTSFactory.is_available(engine_id)
            status = "[green]installed[/green]" if available else "[red]not installed[/red]"
            console.print(f"  {engine_id}: {display_name} ({status})")
        console.print("")
        return

    # Validate required arguments for generation
    if not args.input_voice or not args.text or not args.output_file:
        parser.print_help()
        console.print("\n[red]Error:[/red] -i, -t, and -o are required for audio generation.")
        return

    # Ensure the directory for the output file exists
    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        logger.info("[bold cyan]Initializing VoiceCloner[/bold cyan]")
        logger.info(f"  Engine: {args.engine}")
        logger.info(f"  Reference voice: {args.input_voice}")

        # Build engine-specific kwargs
        engine_kwargs = {"language": args.language}

        if args.engine == "coqui":
            engine_kwargs["temperature"] = args.temperature
        elif "chatterbox" in args.engine:
            engine_kwargs["cfg_weight"] = args.cfg_weight
            engine_kwargs["exaggeration"] = args.exaggeration

        # Create cloner
        cloner = VoiceCloner(speaker_wav=args.input_voice, engine=args.engine)

        logger.info("[bold green]Generating speech...[/bold green]")
        cloner.say(
            args.text, play_audio=not args.no_play, save_audio=True, output_file=args.output_file, **engine_kwargs
        )

        logger.info(f"[bold green]Speech saved to:[/bold green] {args.output_file}")

    except FileNotFoundError:
        logger.error(f"[bold red]Error:[/bold red] Input voice file not found: {args.input_voice}")
    except ImportError as e:
        logger.error(f"[bold red]Missing dependency:[/bold red] {e}")
        logger.info("Install required package with: pip install <package-name>")
    except Exception as e:
        logger.error(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
