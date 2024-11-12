# AnimeSaturn Downloader

> A Python-based tool for downloading anime series from AnimeSaturn, featuring progress tracking for each episode. It efficiently extracts video URLs and manages downloads.

![Screenshot](https://github.com/Lysagxra/AnimeSaturnDownloader/blob/8f8cf230cb28bc37d0004bded26d2fcf9344427d/misc/Screenshot.png)

## Features

- Downloads multiple episodes concurrently.
- Supports batch downloading via a list of URLs.
- Tracks download progress with a progress bar.
- Supports downloading from alternative hosts if necessary.
- Automatically creates a directory structure for organized storage.

## Directory Structure

```
project-root/
├── helpers/
│ ├── download_utils.py   # Script containing utilities for managing the download process
│ ├── format_utils.py     # Script containing formatting utilities
│ ├── progress_utils.py   # Script containing utilities for tracking download progress
│ └── streamtape2curl.py  # Module for extracting download links from alternative hosts
├── anime_downloader.py   # Module for downloading anime episodes
├── main.py               # Main script to run the downloader
└── URLs.txt              # Text file containing anime URLs
```

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lysagxra/AnimeSaturnDownloader.git

2. Navigate to the project directory:
   ```bash
   cd AnimeSaturnDownloader

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Single Anime Download

To download a single anime, you can use the `anime_downloader.py` script.

### Usage

Run the script followed by the anime URL you want to download:

```bash
python3 anime_downloader.py <anime_url>
```

### Example

```bash
python3 anime_downloader.py https://www.animesaturn.cx/anime/Dan-Da-Dan
```

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the anime URLs you want to download.

2. Run the main script via the command line:

```bash
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
