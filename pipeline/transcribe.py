from __future__ import annotations

import warnings

import click
import whisper
import requests
from rich import print

from pipeline import settings, utils

warnings.filterwarnings("ignore")


@click.command()
@click.option(
    "-f",
    "--file",
    type=str,
    help="The uuid of the mp3 file to transcribe",
)
@click.option(
    "-m",
    "--model",
    default="turbo",
    type=click.Choice(
        ["tiny", "base", "small", "medium", "large", "turbo"], case_sensitive=False
    ),
    help="Model to use for transcription",
)
def transcribe(file: str, model: str) -> None:
    """
    Transcribe a single audio file using OpenAI's Whisper.
    
    This function demonstrates the core transcription workflow:
    1. Select an audio file (specific or random untranscribed)
    2. Download the audio file with streaming (memory-efficient)
    3. Load the appropriate Whisper model
    4. Perform speech-to-text transcription
    5. Save the result as a text file
    6. Clean up temporary files
    
    The streaming download and temporary file approach allows processing
    of large audio files without running out of disk space or memory.
    """
    print("🎤 Starting audio transcription...")
    
    # STEP 1: Select which file to transcribe
    if file:
        print(f"📁 Transcribing specific file: {file}")
        mp3_file = utils.get_mp3_by_uuid(file)
    else:
        print("🎲 Selecting random untranscribed file...")
        mp3_file = utils.get_untranscribed_mp3()
    
    print(f"📋 Selected: {mp3_file['title']}")
    print(f"🆔 File ID: {mp3_file['page_id']}")

    # STEP 2: Download the audio file using streaming
    # Streaming is crucial for large files - it downloads in chunks
    # rather than loading the entire file into memory at once
    print(f"⬇️  Downloading: [bold]{mp3_file['download_link']}[/bold]")
    r = requests.get(
        mp3_file["download_link"],
        stream=True,  # This enables chunk-by-chunk downloading
        headers={
            # Use a realistic User-Agent to avoid being blocked
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
    )
    r.raise_for_status()  # Raise an exception for HTTP errors
    
    # Create temporary file path for the downloaded audio
    mp3_path = settings.OUTPUT_DIR / f"{mp3_file['page_id']}.mp3"
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download in 8KB chunks to manage memory usage
    with open(mp3_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ Download complete: {mp3_path.stat().st_size / (1024*1024):.1f}MB")

    # STEP 3: Load the Whisper model
    # Models are cached after first load, so subsequent uses are faster
    print(f"🧠 Loading Whisper model: [bold]{model}[/bold]")
    model_obj = whisper.load_model(model)
    print("✅ Model loaded successfully")

    # STEP 4: Perform the actual transcription
    # This is where the magic happens - Whisper converts speech to text
    print(f"🎯 Transcribing: [bold]{mp3_path}[/bold]")
    print("⏳ This may take several minutes depending on file length and model size...")
    
    # verbose=True shows real-time progress during transcription
    result = model_obj.transcribe(str(mp3_path), verbose=True)
    
    print("✅ Transcription complete!")

    # STEP 5: Save the transcription as a text file
    # The result contains the full text plus metadata (timestamps, etc.)
    txt_path = settings.OUTPUT_DIR / f"{mp3_file['page_id']}.txt"
    print(f"💾 Writing transcription: [bold]{txt_path}[/bold]")
    
    with open(txt_path, "w") as f:
        # Extract just the text content and clean up whitespace
        f.write(result["text"].strip())
    
    # Show some stats about the transcription
    word_count = len(result["text"].split())
    print(f"📊 Transcription stats: {word_count} words")

    # STEP 6: Clean up temporary files
    # Delete the downloaded MP3 to save disk space
    mp3_path.unlink()
    print("🗑️  Temporary audio file deleted")

    # Final success message
    print("🎉 Transcription complete and saved!")
    print(f"📄 Output file: {txt_path}")


if __name__ == "__main__":
    transcribe()
