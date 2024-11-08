"""
This module provides utility functions for processing and formatting
anime-related strings and URLs. It includes functions for checking and
removing specific patterns from strings, extracting anime IDs from URLs,
and formatting anime names by removing designated substrings.
"""

import re
from urllib.parse import urlparse

PATTERN = r"-a+$"
ENDSTRINGS = ["Sub ITA", "ITA"]

def ends_with_pattern(main_string):
    """
    Check if a string ends with the pattern "-a...a", where 'a...' means one or
    more 'a' characters.

    Args:
        main_string (str): The string to check.

    Returns:
        bool: True if the string ends with the pattern, False otherwise.
    """
    match = re.search(PATTERN, main_string)
    return match is not None

def remove_pattern(main_string):
    """
    Remove the substring of the type "-a...a" from the end of a main string.

    Args:
        main_string (str): The string from which to remove the substring.

    Returns:
        str: The string with the specified substring removed from the end.
    """
    return re.sub(PATTERN, '', main_string)

def extract_anime_id(url):
    """
    Extracts the Anime ID from a given URL.

    Args:
        url (str): The URL of the anime page.

    Returns:
        str: The extracted Anime ID from the URL.

    Raises:
        ValueError: If the URL format is invalid or the Anime ID cannot be
                    extracted.
    """
    try:
        parsed_url = urlparse(url)
        anime_id = parsed_url.path.split('/')[-1]

        if ends_with_pattern(anime_id):
            anime_id = remove_pattern(anime_id)

#        domain = parsed_url.netloc.split('.')[-1]
        return anime_id

    except IndexError as indx_err:
        raise ValueError("Invalid URL format.") from indx_err

def extract_anime_name(soup):
    """
    Extracts the anime name from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed
                              HTML content.

    Returns:
        tuple: A tuple containing the Anime ID and domain.

    Raises:
        ValueError: If the container with the specified class is not found in
                    the BeautifulSoup object.
        AttributeError: If there is an error extracting the anime name.
    """
    try:
        container = soup.find(
            'div', {'class': "container anime-title-as mb-3 w-100"}
        )

        if container is None:
            raise ValueError("Anime title container not found.")

        return container.find('b').get_text()

    except AttributeError as attr_err:
        return AttributeError(f"Error extracting anime name: {attr_err}")

def format_anime_name(anime_name):
    """
    Formats the anime name by removing specific substrings that may appear
    at the end.

    Args:
        anime_name (str): The anime name extracted from the page.

    Returns:
        str: The formatted anime name.

    Raises:
        ValueError: If the anime name format is invalid.
    """
    def remove_substrings_at_end(string, substrings):
        """
        Removes specific substrings from the end of a string.

        Args:
            string (str): The string from which to remove substrings.
            substrings (list): A list of substrings to remove from the end.

        Returns:
            str: The string with any matching substrings removed.
        """
        for substring in substrings:
            if string.endswith(substring):
                return string[:-len(substring)].strip()
        return string

    try:
        return remove_substrings_at_end(anime_name, ENDSTRINGS)

    except IndexError as indx_err:
        raise ValueError("Invalid Anime name format.") from indx_err
