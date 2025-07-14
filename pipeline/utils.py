from __future__ import annotations

import json
import random

from pipeline import settings


def get_all_mp3() -> list:
    """
    Load all available MP3 metadata from the scraped JSON file.
    
    This function serves as the central data source for the entire pipeline.
    It reads the structured data created by the scraping process and makes
    it available to other parts of the system.
    
    Returns:
        list: List of dictionaries, each containing metadata for one broadcast:
              - page_id: Unique identifier for the broadcast
              - title: Human-readable title of the broadcast
              - description: Brief description of the content
              - download_link: Direct URL to the MP3 file
              - href: Original detail page URL
              - page: Which list page this was found on
    """
    # Load the JSON file created by the scraping process
    json_path = settings.INPUT_DIR / "json" / "pages.json"
    
    # This file should exist after running the scrape command
    if not json_path.exists():
        raise FileNotFoundError(
            f"Scraped data not found at {json_path}. "
            "Run 'uv run python -m pipeline.scrape' first."
        )
    
    with open(json_path) as file:
        mp3_list = json.load(file)

    return mp3_list


def get_all_untranscribed_mp3() -> list:
    """
    Filter the complete MP3 list to only untranscribed files.
    
    This function implements the core logic for tracking transcription progress.
    It uses the file system as a simple database - if a .txt file exists for
    a given page_id, we consider that broadcast transcribed.
    
    This approach is simple but effective for this use case:
    - No separate database needed
    - Easy to see progress by looking at the output directory
    - Resilient to interruptions (can resume where left off)
    - Works well with version control (text files can be committed)
    
    Returns:
        list: Subset of get_all_mp3() containing only untranscribed files
    """
    # Get the complete list of available broadcasts
    all_mp3s = get_all_mp3()
    
    # Filter to only those without existing transcriptions
    # This uses a list comprehension with a helper function
    untranscribed = [
        mp3 for mp3 in all_mp3s 
        if not transcription_exists(mp3["page_id"])
    ]

    return untranscribed


def get_untranscribed_mp3() -> dict:
    """
    Select a random untranscribed file for processing.
    
    This function is used when no specific file is requested - it picks
    a random file from the untranscribed list. This randomization helps
    distribute the workload when multiple processes are running in parallel
    (like in GitHub Actions matrix jobs).
    
    Random selection also means you'll get a variety of content types
    and time periods, which is useful for testing and development.
    
    Returns:
        dict: Single broadcast metadata dictionary
        
    Raises:
        IndexError: If no untranscribed files are available
    """
    # Get all files that still need transcription
    untranscribed_list = get_all_untranscribed_mp3()
    
    # Check if there are any files left to transcribe
    if not untranscribed_list:
        raise IndexError(
            "No untranscribed files available. All broadcasts have been processed!"
        )

    # Select a random file from the available options
    # This helps distribute work across parallel processes
    selected_file = random.choice(untranscribed_list)

    return selected_file


def get_mp3_by_uuid(page_id: str) -> dict:
    """
    Retrieve metadata for a specific broadcast by its unique identifier.
    
    This function enables targeted transcription of specific files, which is
    useful for:
    - Retrying failed transcriptions
    - Processing high-priority content first
    - Testing with known files
    - Manual quality control
    
    Args:
        page_id (str): The unique identifier for the broadcast
        
    Returns:
        dict: Broadcast metadata dictionary
        
    Raises:
        StopIteration: If no broadcast with the given ID is found
    """
    try:
        # Search through all available broadcasts for matching ID
        # Using next() with a generator expression for efficiency
        mp3_file = next(
            mp3 for mp3 in get_all_mp3() 
            if mp3["page_id"] == page_id
        )
        return mp3_file
    
    except StopIteration:
        # Provide a helpful error message if the ID isn't found
        raise ValueError(
            f"No broadcast found with ID '{page_id}'. "
            "Check that the ID is correct and the scraping data is up to date."
        )


def transcription_exists(page_id: str) -> bool:
    """
    Check whether a transcription file already exists for a given broadcast.
    
    This function implements our simple "file system as database" approach
    for tracking transcription progress. The naming convention is:
    - Input: page_id (e.g., "abc123")  
    - Output file: "IO_{page_id}.txt" (e.g., "IO_abc123.txt")
    
    The "IO_" prefix helps distinguish transcription files from other
    text files and makes them easy to identify and manage.
    
    This approach has several advantages:
    - No database setup required
    - Progress is visible in the file system
    - Easy to manually inspect or delete specific transcriptions
    - Works well with version control
    - Resilient to process interruptions
    
    Args:
        page_id (str): The unique identifier for the broadcast
        
    Returns:
        bool: True if transcription file exists, False otherwise
    """
    # Construct the expected path for the transcription file
    txt_path = settings.OUTPUT_DIR / f"IO_{page_id}.txt"

    # Check if the file exists in the file system
    # This is our simple way of tracking what's been transcribed
    return txt_path.exists()
