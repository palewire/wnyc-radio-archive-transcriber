from __future__ import annotations

import click
from rich import print

from pipeline import utils


@click.command()
def count() -> None:
    """Print out many untranscribed mp3 files there are."""
    # Get the number of untranscribed mp3 files
    untranscribed = len(utils.get_all_untranscribed_mp3())

    # Get the total number of mp3 files
    total = len(utils.get_all_mp3())

    # Calculate how many are transcribed
    transcribed = total - untranscribed

    # Print a report on the progress
    print(f"Transcribed: {transcribed}/{total} ({transcribed / total:.2%})")


if __name__ == "__main__":
    count()
