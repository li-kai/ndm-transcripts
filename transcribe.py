import os
from pathlib import Path

from google import genai

api_key = os.getenv("GEMINI_API_KEY")
assert api_key is not None
client = genai.Client(api_key=api_key)

# Define the default output directory for transcripts
DEFAULT_TRANSCRIPT_DIR = Path("./ndm_transcripts")

def transcribe_audio(audio_file_path: str) -> str:
    file = client.files.upload(file=audio_file_path)

    model = "gemini-2.5-flash-preview-04-17"
    response = client.models.generate_content(
        model=model,
        contents=[
            "Transcribe this podcast, with speaker diarization. No timestamps.",
            file,
        ],
    )
    return response.text


if __name__ == "__main__":
    # Ensure the transcript directory exists
    DEFAULT_TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    audio_source_dir = Path("./ndm_episodes")
    # Grep all files in the directory ending in .mp3
    if not audio_source_dir.is_dir():
        print(f"Audio source directory {audio_source_dir} not found.")
        exit()

    for file_path in audio_source_dir.iterdir():
        if file_path.suffix == ".mp3":
            transcript = transcribe_audio(str(file_path))
            # Save the transcript to a file
            name = file_path.stem
            output_file_path = DEFAULT_TRANSCRIPT_DIR / f"{name}.txt"
            with open(output_file_path, "w") as f:
                f.write(transcript)
            print(f"Transcript saved to {output_file_path}")
