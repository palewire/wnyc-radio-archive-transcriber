from __future__ import annotations

import json
import random

from pipeline import settings


def get_all_mp3() -> list:
    """Get all mp3 files."""
    # Read in the JSON file
    json_path = settings.INPUT_DIR / "audio.json"
    with open(json_path) as file:
        mp3_list = json.load(file)

    # Return the mp3 list
    return mp3_list


def get_all_untranscribed_mp3() -> list:
    """Get all mp3 files that haven't been transcribed yet."""
    # Filter the list to the files that don't exist
    mp3_list = [mp3 for mp3 in get_all_mp3() if not transcription_exists(mp3["uuid"])]

    # Return the mp3 list
    return mp3_list


def get_untranscribed_mp3() -> dict:
    """Get a random mp3 file that hasn't been transcribed yet."""
    # Get all untranscribed mp3 files
    mp3_list = get_all_untranscribed_mp3()

    # Pull out a random mp3 file
    mp3_file = random.choice(mp3_list)

    # Return the mp3 file
    return mp3_file


def get_mp3_by_uuid(uuid: str) -> dict:
    """Get an mp3 file by UUID.

    Args:
        uuid (str): The UUID of the mp3 file to get.

    Returns:
        dict: The mp3 file with the given UUID.
    """
    # Find the mp3 file by UUID
    mp3_file = next(mp3 for mp3 in get_all_mp3() if mp3["uuid"] == uuid)

    # Return the mp3 file
    return mp3_file


def transcription_exists(uuid: str) -> bool:
    """Check if a transcription exists for a given UUID.

    Args:
        uuid (str): The UUID of the mp3 file to check.

    Returns:
        bool: Whether a transcription exists for the given UUID.
    """
    # Set the path to the txt file
    txt_path = settings.OUTPUT_DIR / f"{uuid}.txt"

    # Return whether the file exists
    return txt_path.exists()
