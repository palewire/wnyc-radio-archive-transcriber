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
    """Transcribe audio from microphone."""
    # Get a random mp3 file
    if file:
        mp3_file = utils.get_mp3_by_uuid(file)
    else:
        mp3_file = utils.get_untranscribed_mp3()

    # Download the mp3 file using a streaming request
    print(f"Downloading: [bold]{mp3_file['download_link']}[/bold]")
    r = requests.get(
        mp3_file["download_link"],
        stream=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
    )
    r.raise_for_status()
    mp3_path = settings.OUTPUT_DIR / f"{mp3_file['page_id']}.mp3"
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mp3_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    # Load the model
    print(f"Loading model: [bold]{model}[/bold]")
    model_obj = whisper.load_model(model)

    # Transcribe it
    print(f"Transcribing: [bold]{mp3_path}[/bold]")
    result = model_obj.transcribe(str(mp3_path), verbose=True)

    # Write it to a txt file in the output dir
    txt_path = settings.OUTPUT_DIR / f"{mp3_file['page_id']}.txt"
    print(f"Writing: [bold]{txt_path}[/bold]")
    with open(txt_path, "w") as f:
        f.write(result["text"].strip())

    # Delete the mp3 file
    mp3_path.unlink()

    # Print the result
    print("Done!")


if __name__ == "__main__":
    transcribe()
