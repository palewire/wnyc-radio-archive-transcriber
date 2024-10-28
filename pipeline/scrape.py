from __future__ import annotations

import json
from pathlib import Path

import click
import requests
from rich import print
from retry import retry
from bs4 import BeautifulSoup

from pipeline import settings


@click.group()
def cli():
    """Scrape the internet for mp3 files."""
    pass


@cli.command()
def html():
    """Download HTML files from the NYC archive site."""
    # Get the number of pages
    page_count = _get_page_count()
    page_list = list(range(1, page_count + 1))

    # Loop through the pages
    for page in page_list:
        _get_page_list(page)

    # Open each of the downloaded HTML files
    dict_list = []
    for page in page_list:
        dict_list += _scrape_page_list(page)

    # Download all the detail pages
    for page in dict_list:
        _get_page_detail(page)
        _scrape_page_detail(page)

    # Write the list of dicts to a JSON file
    json_output_path = settings.INPUT_DIR / "json" / "pages.json"
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing {len(dict_list)} entries to {json_output_path}...")
    with open(json_output_path, "w") as file:
        json.dump(dict_list, file, indent=2)


def _scrape_page_detail(page: dict) -> dict:
    """Scrape the provided detail page."""
    # Let em know we're scraping the page
    print(f"Scraping detail page {page['page_id']}...")

    # Read in the HTML for this page
    html_input_path = (
        settings.INPUT_DIR / "html" / "details" / f"{page['page_id']}.html"
    )

    # Get the HTML
    with open(html_input_path) as file:
        html = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Get the <a> tag with .fa-download class
    download_link = soup.find("a", class_="fa-download")["href"]

    # Add it to the dict
    page["download_link"] = download_link

    # Return the dict
    return page


def _scrape_page_list(page: int) -> list[dict]:
    """Scrape a list of entries from the provided page."""
    # Let em know we're scraping the page
    print(f"Scraping page {page}...")

    # Read in the HTML for this page
    html_input_path = settings.INPUT_DIR / "html" / "lists" / f"page_{page}.html"

    # Get the HTML
    with open(html_input_path) as file:
        html = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Get the #search-results element
    search_results = soup.find("div", id="search-results")

    # Get a list of the .result-item elements
    result_items = search_results.find_all("div", class_="result-item")

    # Loop through them
    dict_list = []
    for item in result_items:
        # Get the title from the <h5> tag
        title = item.find("h5").text

        # Get the href from the a tag inside the <h5> tag
        href = item.find("h5").find("a")["href"]

        # Parse the id from the href
        page_id = href.split("/")[-2]
        assert page_id.strip()

        # Get the description from the .archive_description p element
        description = item.find("div", class_="archive_description").p.text

        # Toss it in a dict
        entry = {
            "page_id": page_id.strip(),
            "title": title.strip(),
            "href": href.strip(),
            "description": description.strip(),
            "page": page,
        }

        # Append it to the list
        dict_list.append(entry)

    # Return the list of dicts
    return dict_list


@retry(tries=3, delay=3, backoff=2)
def _get_page_detail(page: dict) -> Path:
    """Scrape the provided page."""
    # Set the HTML output path
    html_output_path = (
        settings.INPUT_DIR / "html" / "details" / f"{page['page_id']}.html"
    )

    # If the file already exists, return it
    if html_output_path.exists():
        print(f"HTML for page {page['page_id']} already exists")
        return html_output_path

    # Let em know we're getting the HTML
    print(f"Getting HTML for detail page {page['page_id']}...")

    # Make sure the parent directory exists
    html_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get the HTML
    r = requests.get(page["href"])
    assert r.ok

    # Write the prettified HTML to a file
    with open(html_output_path, "w") as file:
        file.write(BeautifulSoup(r.text, "html.parser").prettify())

    # Return the HTML output path
    return html_output_path


def _get_page_list(page: int) -> Path:
    """Get the HTML for a page from the NYC archive site."""
    # Set the HTML output path
    html_output_path = settings.INPUT_DIR / "html" / "lists" / f"page_{page}.html"

    # If the file already exists, return it
    if html_output_path.exists():
        print(f"HTML for page {page} already exists")
        return html_output_path

    # Let em know we're getting the HTML
    print(f"Getting HTML for page {page}...")

    # Make sure the parent directory exists
    html_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Set the url
    seed_url = "https://nycrecords.access.preservica.com/uncategorized/SO_4574c0f5-03e8-4f9b-a0c6-d1c8ff23759b/"
    params = {
        "pg": page,
    }

    # Get the HTML
    r = requests.get(seed_url, params=params)
    assert r.ok

    # Write the prettified HTML to a file
    with open(html_output_path, "w") as file:
        file.write(BeautifulSoup(r.text, "html.parser").prettify())

    # Return the HTML output path
    return html_output_path


def _get_page_count() -> int:
    """Get the number of pages on the NYC archive site."""
    # Let em know we're getting the page count
    print("Getting page count...")

    # Get the seed url
    seed_url = "https://nycrecords.access.preservica.com/uncategorized/SO_4574c0f5-03e8-4f9b-a0c6-d1c8ff23759b/"
    r = requests.get(seed_url)
    assert r.ok

    # Get the HTML
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # Get .pagination
    pagination = soup.find("div", class_="pagination")

    # Get all the <a> tags with a .page-numbers class
    page_numbers = pagination.find_all("a", class_="page-numbers")

    # Get the text from each one
    text_list = [
        page_number.text for page_number in page_numbers if page_number.text.isdigit()
    ]

    # Get the max number
    page_count = max([int(text) for text in text_list])

    # Print the page count
    print(f"Discovered {page_count} pages")

    # Return the page count
    return page_count


if __name__ == "__main__":
    cli()
