# Change: Integrate Chatterbox-TTS Model

## Why
The current VoiceCast project is tightly coupled to Coqui TTS's XTTS v2 model, limiting flexibility and access to newer TTS technologies. Chatterbox-TTS offers superior performance with lower VRAM requirements, paralinguistic tag support, and MIT licensing, making it an excellent alternative or complement to the existing Coqui implementation.

## What Changes
- Add Chatterbox-TTS as an optional TTS provider alongside Coqui TTS
- Implement TTS adapter pattern for multi-provider support
- Update dependencies to include chatterbox-tts package
- Add configuration-driven model selection
- Support Chatterbox-Turbo's paralinguistic tags (`[laugh]`, `[cough]`, `[chuckle]`)
- Maintain backward compatibility with existing Coqui TTS implementation
- Add new CLI and GUI options for provider selection

## Impact
- **Affected specs**: voice-cloning (new provider support), tts-generation (enhanced capabilities)
- **Affected code**: voice_cloner.py (core adapter), vcloner.py (CLI), voice_cloning_app.py (GUI), requirements.txt (dependencies)
- **Breaking changes**: None - existing Coqui TTS functionality preserved
- **New capabilities**: Paralinguistic tags, lower VRAM usage, multi-provider architecture
