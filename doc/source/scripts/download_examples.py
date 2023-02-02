"""Script to download examples."""
from pathlib import Path

from bs4 import BeautifulSoup
import requests

# specify the URL of the archive here
archive_url = "https://github.com/executablebooks/sphinx-design/tree/main/docs/snippets/rst"

THIS_PATH = Path(__file__).parent.resolve()

example_path = str((THIS_PATH / "examples.rst").absolute())


def get_example_links():
    """Initialize to get examples link."""
    r = requests.get(archive_url)
    soup = BeautifulSoup(r.content, "html5lib")
    links = soup.findAll("a")
    example_links = [
        "https://raw.githubusercontent.com" + link["href"]
        for link in links
        if link["href"].endswith("txt")
    ]
    raw_link = [w.replace("/blob/", "/") for w in example_links]
    return raw_link


def download_example_series(example_links):
    """Initialize to download examples."""
    with open(example_path, "wb") as f:
        for link in example_links:
            r = requests.get(link)
            f.write(r.content)
    return


if __name__ == "__main__":

    # getting all example links
    example_links = get_example_links()

    # download all examples
    download_example_series(example_links)
