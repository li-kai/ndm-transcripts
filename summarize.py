import logging
import os
import time
from pathlib import Path

from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SOURCE_DIRECTORY = Path(".")
TARGET_SUFFIX = ".summary.txt"
TRANSCRIPT_SUFFIX = ".txt"
# Consider using a more capable model for better results, e.g., "gemini-1.5-pro-preview-0514"
MODEL_NAME = "gemini-2.5-flash-preview-04-17" # Faster, cheaper option

# --- Helper Functions ---

def initialize_genai_client(api_key: str | None) -> genai.Client:
    """Initializes and returns the Gemini API client."""
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set.")
        raise ValueError("API key is missing. Please set the GEMINI_API_KEY environment variable.")
    try:
        client = genai.Client(api_key=api_key)
        logging.info("Gemini client initialized successfully.")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Gemini client: {e}")
        raise

def read_file_content(file_path: Path) -> str:
    """Reads and returns the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return "" # Return empty string to allow skipping the file

def write_to_file(file_path: Path, content: str):
    """Writes content to a file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Successfully wrote to {file_path}")
    except IOError as e:
        logging.error(f"Error writing to file {file_path}: {e}")


def generate_summary(transcript: str, client: genai.Client, model_name: str) -> str:
    """Generates a summary and actionable takeaways using the Gemini API."""
    prompt = f"""Analyze the following podcast transcript. Identify the core arguments, key insights, and actionable takeaways, specifically focusing on aspects valuable to a determined solo entrepreneur aiming for significant impact.

Extract the most potent information, discarding fluff. Present the main points clearly and concisely. What is the single most important lesson or strategy discussed?

Transcript:
---
{transcript}
---

Summary and Takeaways:"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return "Error: Could not generate summary."

def extract_guest_info(transcript: str, client: genai.Client, model_name: str) -> str:
    """Extracts guest information using the Gemini API."""
    prompt = f"""From the provided podcast transcript, identify the primary guest speaker(s). For each guest:
1.  Provide their full name.
2.  State their job title.
3.  Mention their affiliated company or organization.
4.  Access your knowledge base and add any notable background information, context, or achievements associated with this individual relevant to the discussion. If none, state "No additional background information found."
5.  Summarize the primary topic discussed with the guest in one concise sentence.

Format the output clearly for each guest.

Transcript:
---
{transcript}
---

Guest Information:"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error extracting guest info: {e}")
        return "Error: Could not extract guest information."


# --- Main Execution Logic ---

def process_transcripts(source_dir: Path, client: genai.Client, model: str):
    """Processes all transcript files in the source directory."""
    logging.info(f"Scanning directory: {source_dir.resolve()}")
    processed_files = 0
    skipped_files = 0

    for item in source_dir.iterdir():
        time.sleep(0.1)
        # Process only .txt files, excluding existing .summary.txt files
        if item.is_file() and item.suffix == TRANSCRIPT_SUFFIX and not item.stem.endswith(TARGET_SUFFIX.replace(TRANSCRIPT_SUFFIX, '')):

            logging.info(f"Processing transcript: {item.name}")
            target_file_path = source_dir / f"{item.stem}{TARGET_SUFFIX}"

            # Skip if summary file already exists
            if target_file_path.exists():
                logging.warning(f"Summary file already exists, skipping: {target_file_path.name}")
                skipped_files += 1
                continue

            transcript_content = read_file_content(item)
            if not transcript_content:
                logging.warning(f"Transcript file is empty or could not be read, skipping: {item.name}")
                skipped_files +=1
                continue # Skip empty or unreadable files

            # Generate Summary
            logging.info(f"Generating summary for {item.name}...")
            summary = generate_summary(transcript_content, client, model)

            # Extract Guest Info
            logging.info(f"Extracting guest info for {item.name}...")
            guest_info = extract_guest_info(transcript_content, client, model)

            # Combine and Write Output
            output_content = f"""## Summary & Takeaways

{summary}

---

## Guest Information

{guest_info}"""
            write_to_file(target_file_path, output_content)
            processed_files += 1
        elif item.is_file() and item.suffix == TRANSCRIPT_SUFFIX and item.stem.endswith(TARGET_SUFFIX.replace(TRANSCRIPT_SUFFIX, '')):
             logging.debug(f"Skipping already summarized file: {item.name}") # Log skipped summary files at debug level


    logging.info(f"Processing complete. Processed: {processed_files}, Skipped: {skipped_files}")


if __name__ == "__main__":
    gemini_client = initialize_genai_client(GEMINI_API_KEY)
    process_transcripts(SOURCE_DIRECTORY, gemini_client, MODEL_NAME)
