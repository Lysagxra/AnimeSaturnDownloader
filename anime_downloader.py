"""
This script downloads anime episodes from a given AnimeSaturn URL.

It extracts the anime ID, formats the anime name, retrieves episode IDs and
URLs, and downloads each episode.

Dependencies:
    - requests: For making HTTP requests.
    - bs4 (BeautifulSoup): For parsing HTML content.

Custom Modules:
    - streamtape2curl (get_curl_command): For extract the download link from
                                          the alternative host.

Usage:
    - Run the script with the URL of the anime page as a command-line argument.
    - It will create a directory structure in the 'Downloads' folder based on
      the anime name where each episode will be downloaded.
"""

import os
import sys
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
)

from helpers.streamtape2curl import get_curl_command as get_alt_download_link

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"
CHUNK_SIZE = 8192

PATTERN = r"-a+$"
ENDSTRINGS = ["Sub ITA", "ITA"]
WATCH_STR = "watch?file="

COLORS = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/117.0"
    )
}

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
    Extracts the Anime ID from the provided URL and determines the domain of
    the host page.

    Args:
        url (str): The URL of the anime page.

    Returns:
        tuple: A tuple containing the Anime ID and domain.

    Raises:
        ValueError: If the URL format is invalid.
    """
    try:
        parsed_url = urlparse(url)
        anime_id = parsed_url.path.split('/')[-1]

        if ends_with_pattern(anime_id):
            anime_id = remove_pattern(anime_id)

        domain = parsed_url.netloc.split('.')[-1]
        return anime_id, domain

    except IndexError:
        raise ValueError("Invalid URL format.")

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
    Formats the Anime name by removing specific substrings at the end.

    Args:
        anime_name (str): The Anime name extracted from the page.

    Returns:
        str: The formatted Anime name.

    Raises:
        ValueError: If the Anime name format is invalid.
    """
    def remove_substrings_at_end(string, substrings):
        for substring in substrings:
            if string.endswith(substring):
                return string[:-len(substring)]
        return string

    try:
        return remove_substrings_at_end(anime_name, ENDSTRINGS)

    except IndexError:
        raise ValueError("Invalid Anime name format.")

def get_episode_urls(soup, match, watch_url=False):
    """
    Extract URLs from a BeautifulSoup object based on the given criteria.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML.
        match (str): The string to match within the attribute.

    Returns:
        str or list: The first matching URL if watch_url is True,
                     otherwise a list of URLs.
    """
    if not watch_url:
        links = soup.find_all(
            'a',
            {
                'href': True,
                'target': "_blank",
                'class': "btn btn-dark mb-1 bottone-ep"
            }
        )
        return [link.get('href') for link in links]

    links = soup.find_all('a')
    filtered_links = list(filter(lambda link: match in link['href'], links))
    return filtered_links[0].get('href')

def get_video_urls(episode_urls, match):
    """
    Retrieves video URLs from a list of episode URLs.

    Args:
        episode_urls (list): A list of episode URLs.
        match (str): The string to match within the attribute.

    Returns:
        list: A list of video URLs.

    Raises:
        requests.RequestException: If an error occurs while making an
                                   HTTP request.
    """
    def extract_video_url(episode_url):
        try:
            response = requests.get(episode_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            video_url = get_episode_urls(soup, match, watch_url=True)
            return video_url if video_url else None

        except requests.RequestException as req_err:
            print(f"Error fetching episode URL {episode_url}: {req_err}")
            return None

    return [
        url for url in map(extract_video_url, episode_urls)
        if url is not None
    ]

def extract_download_link(video_link):
    """
    Extracts the download link from a video source tag.

    Args:
        video_link (Tag): The BeautifulSoup Tag object representing the video
                          source.

    Returns:
        str: The extracted download link.

    Raises:
        KeyError: If the 'src' attribute is not present in the tag.
    """
    try:
        return video_link['src']

    except KeyError as key_err:
        raise KeyError(f"Expected attribute not found: {key_err}")

def get_episode_file_name(episode_download_link):
    """
    Extract the file name from the provided episode download link.

    Args:
        episode_download_link (str): The download link for the episode.

    Returns:
        str: The extracted file name, or None if the link is None or empty.
    """
    try:
        return episode_download_link.split('/')[-1] \
            if episode_download_link else None

    except IndexError as indx_err:
        print(f"Error while extracting the file name: {indx_err}")

def download_episode(
        download_link, download_path, job_progress, task,
        overall_task, is_default_host=True
):
    """
    Downloads an episode from the specified link and provides progress updates.

    Args:
        index (int): The index of the episode (0-based).
        num_episodes (int): The total number of episodes available.
        download_link (str): The URL from which to download the episode.
        download_path (str): The directory path where the episode file will be
                             saved.
        is_default_host (bool): Indicates whether the default host is being
                                used. Defaults to True.

    Prints:
        Progress messages during the download process.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
        OSError: If there is an error with file operations, such as writing to
                 disk.
        ValueError: If the content-length is invalid or not provided in the
                    response headers.
    """
    try:
        response = requests.get(download_link, stream=True, headers=HEADERS)
        response.raise_for_status()

        file_name = get_episode_file_name(download_link)
        final_path = os.path.join(download_path, file_name) \
            if is_default_host else download_path
        file_size = int(response.headers.get('content-length', -1))
        total_downloaded = 0

        with open(final_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    total_downloaded += len(chunk)
                    progress_percentage = (total_downloaded / file_size) * 100
                    job_progress.update(task, completed=progress_percentage)

        job_progress.update(task, completed=100, visible=False)
        job_progress.advance(overall_task)

    except requests.RequestException as req_error:
        print(f"HTTP request failed: {req_error}")

    except OSError as os_error:
        print(f"File operation failed: {os_error}")

def get_alt_video_url(url):
    """
    Retrieves an alternative video URL by appending a server parameter to the
    original URL.

    Args:
        url (str): The original video URL to be processed.

    Returns:
        str: The alternative video URL found in the anchor tag.

    Raises:
        requests.RequestException: If there is an issue with the GET request.
        IndexError: If no valid anchor tags are found in the response.
    """
    alt_url = url + "&server=1"

    try:
        response = requests.get(alt_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        anchor_tag = soup.find('a', {'href': True, 'target': "_blank"})

        if not anchor_tag:
            raise IndexError("No tags found with the target '_blank'.")

        return anchor_tag['href']

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

    except IndexError as indx_err:
        print(f"Error finding alternative video URL: {indx_err}")

def download_from_alt_host(url, download_path, job_progress, task, overall_task):
    """
    Downloads a video from an alternative host by retrieving the alternative
    video URL, generating a cURL command, and downloading the episode to the
    specified path.

    Args:
        url (str): The original video URL to be processed.
        index (int): The index of the episode to be downloaded.
        num_episodes (int): The total number of episodes to be downloaded.
        download_path (str): The directory path where the episode should be
                             downloaded.

    Raises:
        ValueError: If the alternative video URL cannot be retrieved.
    """
    alt_video_url = get_alt_video_url(url)

    if not alt_video_url:
        raise ValueError(f"Failed to retrieve alternative video URL for {url}.")

    (alt_filename, alt_download_link) = get_alt_download_link(alt_video_url)
    alt_download_path = os.path.join(download_path, alt_filename)
    download_episode(
        alt_download_link, alt_download_path, job_progress, task, overall_task,
        is_default_host=False
    )

def process_video_url(
        url, download_path, job_progress, task, overall_task
):
    """
    Processes a video URL to extract and download its associated files.
    If no source links are found, it attempts to download from an alternative
    host.

    Args:
        url (str): The video URL.
        index (int): The index of the episode.
        num_episodes (int): The total number of episodes.
        download_path (str): The path to save the downloaded episode.

    Raises:
        requests.RequestException: If there is an error with the HTTP request
                                   while processing the video URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        video_source = soup.find('source', {'type': "video/mp4", 'src': True})

        if video_source:
            download_link = extract_download_link(video_source)
            download_episode(
                download_link, download_path, job_progress, task, overall_task
            )
        else:
            download_from_alt_host(
                url, download_path, job_progress, task, overall_task
            )

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

def download_anime(anime_name, video_urls, download_path):
    job_progress = create_progress_bar()
    progress_table = create_progress_table(anime_name, job_progress)
    num_episodes = len(video_urls)

    with Live(progress_table, refresh_per_second=10):
        futures = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            overall_task = job_progress.add_task(
                f"[cyan]Progress",
                total=num_episodes, visible=True
            )
            for i, video_url in enumerate(video_urls):
                task = job_progress.add_task(
                    f"[cyan]Episode {i + 1}/{num_episodes}",
                    total=100, visible=False
                )
                future = executor.submit(
                    process_video_url, video_url,
                    download_path, job_progress, task, overall_task
                )
                futures[future] = task

                while futures:
                    for future_task in list(futures.keys()):
                        if future_task.running():
                            task_id = futures.pop(future_task)
                            job_progress.update(task_id, visible=True)

def create_download_directory(download_path):
    """
    Creates a directory for downloads if it doesn't exist.

    Args:
        download_path (str): The path to create the download directory.

    Raises:
        OSError: If there is an error creating the directory.
    """
    try:
        os.makedirs(download_path, exist_ok=True)
    except OSError as os_err:
        print(f"Error creating directory: {os_err}")
        sys.exit(1)

def fetch_anime_page(url):
    """
    Fetches the anime page and returns its BeautifulSoup object.

    Args:
        url (str): The URL of the anime page.

    Returns:
        BeautifulSoup: The BeautifulSoup object containing the HTML.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    except requests.RequestException as req_err:
        print(f"Error fetching the anime page: {req_err}")
        sys.exit(1)

def create_progress_bar():
    """
    Creates and returns a progress bar for tracking download progress.

    Returns:
        Progress: A Progress object configured with relevant columns.
    """
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        '-',
        TimeRemainingColumn()
    )

def create_progress_table(anime_name, job_progress):
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            job_progress,
            title=f"{anime_name}",
            border_style="red",
            padding=(1, 1)
        )
    )
    return progress_table

def process_anime_download(url):
    """
    Download a series of Anime episodes from the specified URL.

    Args:
        url (str): The URL of the Anime series to download.

    Raises:
        ValueError: If there is an issue extracting the Anime ID or name
                    from the URL or the page content.

    Creates:
        A directory for the Anime series in the current working directory,
        where all episodes will be downloaded.
    """
    soup = fetch_anime_page(url)

    try:
        (anime_id, _) = extract_anime_id(url)
        anime_name = format_anime_name(extract_anime_name(soup))

        download_path = os.path.join(os.getcwd(), DOWNLOAD_FOLDER, anime_name)
        create_download_directory(download_path)

        episode_urls = get_episode_urls(soup, anime_id)

        video_urls = get_video_urls(episode_urls, WATCH_STR)
        download_anime(anime_name, video_urls, download_path)

    except ValueError as val_err:
        print(f"Value error: {val_err}")

def main():
    """
    Main function to download anime episodes from a given AnimeSaturn URL.

    Command-line Arguments:
        <anime_url> (str): The URL of the anime page to download episodes from.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {SCRIPT_NAME} <anime_url>")
        sys.exit(1)

    url = sys.argv[1]
    process_anime_download(url)

if __name__ == '__main__':
    main()
