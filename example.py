from voice_cloner import VoiceCloner

if __name__ == "__main__":
    # Initialize VoiceCloner with the TTS model and speaker reference
    cloner = VoiceCloner(speaker_wav="./original_voice.wav")

    # Convert text to speech and play the audio
    cloner.say("This is an example of text-to-speech with a cloned voice and customizable playback speed.")