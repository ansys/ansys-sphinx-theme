"""Sample module to download examples."""
from bs4 import BeautifulSoup
import requests

# specify the URL of the archive here
archive_url = "https://github.com/executablebooks/sphinx-design/tree/main/docs/snippets/rst"


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
    words = [w.replace("/blob/", "/") for w in example_links]
    return words


def download_example_series(example_links):
    """Initialize to download examples."""
    file_name = "some_file.rst"
    with open(file_name, "wb") as f:
        for link in example_links:
            print("Downloading file:%s" % file_name)
            r = requests.get(link)
            f.write(r.content)
            print("%s downloaded!\n" % link)
    print("All examples downloaded!")
    return


#

if __name__ == "__main__":

    # getting all example links
    example_links = get_example_links()

    # download all examples
    download_example_series(example_links)
