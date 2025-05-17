# ndm-transcripts

This project provides a suite of Python scripts to download, transcribe, and summarize episodes of the 'Naturalistic Decision Making' podcast.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ndm-transcripts
    ```

2.  **Create a virtual environment and install dependencies:**
    It's recommended to use a virtual environment. This project uses `uv` for package management, but you can use `pip` as well.
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    # Or, if you have uv installed:
    # uv pip install -r requirements.txt
    ```

3.  **Set up API Key:**
    These scripts use the Google Gemini API. You need to set your API key as an environment variable:
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Add this line to your shell configuration file (e.g., `.zshrc`, `.bashrc`) to make it permanent.

## Usage

### 1. Download Podcast Episodes

The `download.py` downloads podcast episodes from the RSS feed.

```bash
python download.py [feed_url] [output_folder]
```

-   `feed_url` (optional): The URL of the podcast RSS feed. Defaults to `https://anchor.fm/s/1b3c2204/podcast/rss`.
-   `output_folder` (optional): The directory to save downloaded episodes. Defaults to `ndm_episodes`.

**Options:**
-   `--dry-run`: List episodes without downloading.
-   `--test`: Run internal tests and exit.

**Example:**
```bash
python download.py
# Downloads to ./ndm_episodes/
```

### 2. Transcribe Episodes

The `transcribe.py` script transcribes downloaded `.mp3` files from the `./ndm_episodes/` directory and saves the transcripts as `.txt` files into the `./ndm_transcripts/` directory by default.

```bash
python transcribe.py
```
Make sure your audio files are in the `ndm_episodes` directory. The script will create the `./ndm_transcripts/` directory if it doesn't exist. Transcripts will be saved with the same base name as the audio file.

### 3. Summarize Transcripts

The `summarize.py` script processes `.txt` transcript files from the `./ndm_transcripts/` directory by default. It generates summaries and extracts guest information, then saves them as `.summary.txt` files into the `./ndm_summaries/` directory.

```bash
python summarize.py
```

**Configuration (within `summarize.py`):**
-   `SOURCE_DIRECTORY`: Directory containing transcript files (defaults to `./ndm_transcripts/`).
-   `DEFAULT_SUMMARY_DIR`: Directory where summary files will be saved (defaults to `./ndm_summaries/`).
-   `MODEL_NAME`: Gemini model to use (e.g., "gemini-2.5-flash-preview-04-17").

The script will create the `./ndm_summaries/` directory if it doesn't exist and will skip transcripts for which a summary file already exists in the output directory.

## Workflow

A typical workflow would be:

1.  Run `python download.py` to download new episodes (saved to `./ndm_episodes/`).
2.  Run `python transcribe.py` to transcribe the downloaded audio files (transcripts saved to `./ndm_transcripts/`).
3.  Run `python summarize.py` to create summaries from the new transcripts (summaries saved to `./ndm_summaries/`).
