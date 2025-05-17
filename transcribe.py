import os

from google import genai

api_key = os.getenv("GEMINI_API_KEY")
assert api_key is not None
client = genai.Client(api_key=api_key)

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
    # Grep all files in the directory ending in .mp3
    for file in os.listdir("./ndm_episodes"):
        if file.endswith(".mp3"):
            transcript = transcribe_audio(f"./ndm_episodes/{file}")
            # Save the transcript to a file
            name = file.split(".")[0]
            with open(f"{name}.txt", "w") as f:
                f.write(transcript)
