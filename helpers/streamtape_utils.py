"""
This module provides functionality to extract specific information from the
HTML content of a given Streamtape URL and constructs a cURL command to
download a file from the Streamtape website.
"""

#!/usr/bin/env python
import re
import sys
import requests

PREFIX = "https:/"
NOROBOT_TOKEN_PATTERN = (
    r".*document.getElementById.*\('norobotlink'\).innerHTML =.*?token=(.*?)'.*?;"
)
LINK_TOKEN_PATTERN = (
    r'.*<div id="ideoooolink" style="display:none;">(.*?token=).*?<[/]div>'
)
TITLE_PATTERN = r'.*<meta name="og:title" content="(.*?)">'

def get_curl_command(url):
    """
    Extracts specific information from the HTML content of a given URL and
    constructs a final URL and the original title.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        tuple: A tuple containing the original filename (str) and the
               final URL (str).
    """
    html = requests.get(url, timeout=10).content.decode()

    token = re.match(
        NOROBOT_TOKEN_PATTERN, html, re.M|re.S
    ).group(1)

    infix = re.match(
        LINK_TOKEN_PATTERN, html, re.M|re.S
    ).group(1)

    download_url = f'{PREFIX}{infix}{token}'

    filename = re.match(
        TITLE_PATTERN, html, re.M|re.S
    ).group(1)

    return filename, download_url

def main():
    """
    Main function to process URLs provided as command-line arguments and print
    cURL commands to download files from the Streamtape website.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <url>...", file=sys.stderr)
        sys.exit(1)

    for url in sys.argv[1:]:
        try:
            (filename, download_url) = get_curl_command(url)
            command = f"curl -L -o '{filename}' '{download_url}'"
            print(command)

        except ValueError as val_err:
            print(f"ValueError: {val_err}", file=sys.stderr)

if __name__ == '__main__':
    main()
