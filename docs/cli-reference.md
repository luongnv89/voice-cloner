# CLI Reference

The `vcloner` command-line tool provides a convenient way to generate voice-cloned speech from the terminal.

## Installation

After installing VoiceCloner, the CLI is available as:

```bash
# Using the script directly
python vcloner.py [options]

# Or if installed via pip
vcloner [options]
```

## Synopsis

```
vcloner -i <voice_file> -t <text> -o <output_file> [options]
vcloner --list-engines
vcloner --help
```

## Required Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--input_voice` | `-i` | Path to reference voice audio file (WAV/MP3) |
| `--text` | `-t` | Text to convert to speech |
| `--output_file` | `-o` | Path for output audio file |

## Optional Arguments

### General Options

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--engine` | `-e` | `coqui` | TTS engine to use |
| `--language` | `-l` | `en` | Language code |
| `--no-play` | | | Don't play audio after generation |
| `--list-engines` | | | List available engines and exit |
| `--help` | `-h` | | Show help message |

### Coqui-Specific Options

| Argument | Default | Range | Description |
|----------|---------|-------|-------------|
| `--temperature` | `0.7` | 0.1-1.0 | Sampling temperature |

### Chatterbox-Specific Options

| Argument | Default | Range | Description |
|----------|---------|-------|-------------|
| `--cfg-weight` | `0.5` | 0.0-1.0 | CFG weight for text adherence |
| `--exaggeration` | `0.5` | 0.0-1.5 | Expressiveness level |

## Available Engines

| Engine ID | Description |
|-----------|-------------|
| `coqui` | Coqui XTTS v2 - Multilingual, high quality (default) |
| `chatterbox-turbo` | Chatterbox Turbo - Fast, 350M parameters |
| `chatterbox-standard` | Chatterbox Standard - Higher quality, 500M parameters |

Check installed engines:

```bash
python vcloner.py --list-engines
```

## Examples

### Basic Usage

Generate speech with default Coqui engine:

```bash
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Hello, this is a test of voice cloning." \
    -o output.wav
```

### Using Chatterbox Turbo

Fast generation with Chatterbox:

```bash
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "This is generated with Chatterbox Turbo." \
    -o output.wav \
    --engine chatterbox-turbo
```

### Expressive Speech with Paralinguistic Tags

Use emotional expressions (Chatterbox Turbo only):

```bash
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "That's hilarious [laugh]! I can't believe it [gasp]!" \
    -o expressive.wav \
    --engine chatterbox-turbo \
    --cfg-weight 0.3 \
    --exaggeration 0.7
```

Supported tags: `[laugh]`, `[chuckle]`, `[cough]`, `[sigh]`, `[gasp]`, `[yawn]`

### Multilingual Generation

Generate speech in different languages (Coqui only):

```bash
# French
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Bonjour, comment allez-vous?" \
    -o french.wav \
    --language fr

# Spanish
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Hola, cmo ests?" \
    -o spanish.wav \
    --language es

# German
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Guten Tag, wie geht es Ihnen?" \
    -o german.wav \
    --language de
```

### Adjusting Voice Quality

Fine-tune generation parameters:

```bash
# Higher temperature for more variation (Coqui)
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Testing with higher temperature." \
    -o output.wav \
    --temperature 0.9

# Lower CFG for fast speakers (Chatterbox)
python vcloner.py \
    -i ./voice-samples/fast-speaker.wav \
    -t "This speaker talks quickly." \
    -o output.wav \
    --engine chatterbox-turbo \
    --cfg-weight 0.2
```

### Generate Without Playback

Save file without playing:

```bash
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "This will not play automatically." \
    -o output.wav \
    --no-play
```

### Output to Specific Directory

Create output in a subdirectory:

```bash
python vcloner.py \
    -i ./voice-samples/speaker.wav \
    -t "Saving to a specific directory." \
    -o ./outputs/2024/january/speech.wav
```

The directory will be created automatically if it doesn't exist.

## Batch Processing

### Shell Script Example

Process multiple files:

```bash
#!/bin/bash

VOICE="./voice-samples/speaker.wav"
OUTPUT_DIR="./outputs"

mkdir -p "$OUTPUT_DIR"

# Array of texts
texts=(
    "First sentence to process."
    "Second sentence to process."
    "Third sentence to process."
)

for i in "${!texts[@]}"; do
    python vcloner.py \
        -i "$VOICE" \
        -t "${texts[$i]}" \
        -o "$OUTPUT_DIR/output_$((i+1)).wav" \
        --no-play
    echo "Generated: output_$((i+1)).wav"
done
```

### Processing from File

Read texts from a file:

```bash
#!/bin/bash

VOICE="./voice-samples/speaker.wav"
count=1

while IFS= read -r line; do
    if [ -n "$line" ]; then
        python vcloner.py \
            -i "$VOICE" \
            -t "$line" \
            -o "output_${count}.wav" \
            --no-play
        ((count++))
    fi
done < texts.txt
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Missing required arguments |
| 1 | File not found |
| 1 | Missing dependencies |
| 1 | Generation error |

## Environment Variables

The CLI respects standard Python and PyTorch environment variables:

```bash
# Force CPU usage
CUDA_VISIBLE_DEVICES="" python vcloner.py ...

# Specify GPU
CUDA_VISIBLE_DEVICES=0 python vcloner.py ...

# Reduce PyTorch threads
OMP_NUM_THREADS=4 python vcloner.py ...
```

## Troubleshooting

### "Input voice file not found"

Ensure the path to your reference voice file is correct:

```bash
# Check file exists
ls -la ./voice-samples/speaker.wav

# Use absolute path if needed
python vcloner.py -i /full/path/to/speaker.wav ...
```

### "Missing dependency"

Install required packages:

```bash
# Core dependencies
pip install torch torchaudio TTS sounddevice soundfile rich

# For Chatterbox engine
pip install chatterbox-tts
```

### "Engine not available"

Check which engines are installed:

```bash
python vcloner.py --list-engines
```

### Slow Generation

- First run downloads models (~2GB) - subsequent runs are faster
- Use `--engine chatterbox-turbo` for faster generation
- Ensure CUDA is available for GPU acceleration

## See Also

- [API Reference](api-reference.md) - Python API documentation
- [Engines Guide](engines.md) - Detailed engine comparison
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
