from voice_cloner import VoiceCloner

if __name__ == "__main__":
    # Initialize VoiceCloner with the TTS model and speaker reference
    cloner = VoiceCloner(speaker_wav="./voice-samples/jack-sparrow_original.mp3")

    # Convert text to speech and play the audio
    transcripts = [
        "VoiceCloner is a Python library that uses the Coqui TTS library to clone a specific voice and generate speech in that voice"
        # "Hello everyone, and welcome to this presentation about SlideSpeech! SlideSpeech is a powerful tool designed to automate your presentations. Whether you're using a PDF or PPTX file, SlideSpeech can play an audio file for each slide and automatically advance to the next slide once the audio finishes. This tool is perfect for anyone looking to deliver hands-free, professional presentations with ease. Let’s dive into its key features!",
        # "SlideSpeech comes packed with features to make your presentations seamless. First, it offers dynamic slide timing, meaning each slide stays visible for the exact duration of its corresponding audio file. Second, it’s incredibly easy to use—just provide your presentation and audio files, and SlideSpeech does the rest. Third, it’s cross-platform, working on Windows, macOS, and Linux. Finally, it’s customizable, allowing you to tailor it to your specific needs. With SlideSpeech, you can focus on your audience while the script handles the technical details.",
        # "Ready to use SlideSpeech? Here’s how to get started! First, install Python and the required libraries using pip. Next, download the SlideSpeech script and add your presentation and audio files. Finally, run the script, and you’re all set! SlideSpeech is perfect for classroom lectures, business pitches, or even self-running exhibits in museums or kiosks. Try SlideSpeech today and take your presentations to the next level. Thank you for listening, and I hope you find SlideSpeech as useful as I do!"
    ]

    for i, transcript in enumerate(transcripts):
        cloner.say(transcript, language="en", play_audio=False, save_audio=True, speed=1.0)