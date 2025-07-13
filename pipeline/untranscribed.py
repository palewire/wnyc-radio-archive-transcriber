from __future__ import annotations

import json
import click

from pipeline import utils


@click.command()
@click.option(
    "-l",
    "--limit",
    type=int,
    help="The maximum number of files to list",
)
def untranscribed(limit: int | None) -> None:
    """Get a random mp3 file that hasn't been transcribed yet."""
    # Get a list of all the untranscribed mp3 files
    mp3_list = utils.get_all_untranscribed_mp3()

    # Get a list of the uuids
    uuid_list = [mp3["page_id"] for mp3 in mp3_list]

    # If there's a limit, slice the list
    if limit:
        uuid_list = uuid_list[:limit]

    # Print the list of uuids
    click.echo(json.dumps(uuid_list, indent=2))


if __name__ == "__main__":
    untranscribed()
