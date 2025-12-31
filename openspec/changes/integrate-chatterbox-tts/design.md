## Context
The VoiceCast project currently uses Coqui TTS as its sole provider, creating tight coupling and limiting access to newer TTS technologies. Chatterbox-TTS offers compelling advantages including lower VRAM requirements, paralinguistic tag support, and MIT licensing. This design introduces a multi-provider architecture while maintaining backward compatibility.

## Goals / Non-Goals
- **Goals**: Enable multiple TTS providers, add Chatterbox-TTS support, implement paralinguistic tags, maintain existing API compatibility
- **Non-Goals**: Replace Coqui TTS entirely, break existing functionality, require major refactoring of current codebase

## Decisions
- **Decision**: Use adapter pattern for provider abstraction
  - **Why**: Clean separation, easy to extend, minimal impact on existing code
  - **Alternatives considered**: Direct code modification (too invasive), factory pattern only (less flexible)
- **Decision**: Implement configuration-driven provider selection
  - **Why**: User-friendly, supports runtime switching, easy testing
  - **Alternatives considered**: Compile-time selection (less flexible), environment variables (harder to manage)
- **Decision**: Start with Chatterbox-Turbo as primary Chatterbox variant
  - **Why**: Best performance, paralinguistic tags, lower VRAM requirements
  - **Alternatives considered**: Multilingual model (larger), original Chatterbox (less efficient)

## Risks / Trade-offs
- **Risk**: Dependency conflicts between Coqui TTS and Chatterbox-TTS
  - **Mitigation**: Optional dependency handling, separate virtual environments for testing
- **Risk**: Performance differences between providers
  - **Mitigation**: Benchmark testing, provider-specific optimizations
- **Trade-off**: Increased code complexity vs. flexibility
  - **Justification**: Adapter pattern minimizes complexity while providing significant benefits

## Migration Plan
1. **Phase 1**: Implement adapter interface and Coqui wrapper (no breaking changes)
2. **Phase 2**: Add Chatterbox adapter with basic functionality
3. **Phase 3**: Add provider selection and paralinguistic tag support
4. **Phase 4**: Update CLI/GUI and documentation
5. **Rollback**: Keep original Coqui implementation as fallback

## Open Questions
- How to handle provider-specific parameters in unified API?
- Should we expose all Chatterbox controls (CFG weight, exaggeration) or keep simple interface?
- How to manage model downloading and caching across providers?
- What's the best approach for testing audio quality differences?
