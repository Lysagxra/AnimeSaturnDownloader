# Simple AnimeSaturn Downloader

> A Python-based tool for downloading anime from AnimeSaturn.

![Screenshot](https://github.com/Lysagxra/SimpleAnimeSaturnDownloader/blob/f178abf8466a4757c765c623aaf1ebf06d492c77/misc/Screenshot.png)

## Features

- Downloads anime episodes from an AnimeSaturn URL.
- Supports batch downloading via a list of URLs.

## Directory Structure
```
project-root/
├── helpers/
│ └── streamtape2curl.py  # Python script to extract the download link from the alternative host
├── anime_downloader.py   # Python script to download the anime episodes
├── main.py               # Main Python script to run the downloader
└── URLs.txt              # Text file containing album URLs
```

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lysagxra/SimpleAnimeSaturnDownloader.git

2. Navigate to the project directory:
   ```bash
   cd SimpleAnimeSaturnDownloader

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Single Hanime Download

To download a single hanime, you can use the `anime_downloader.py` script.

### Usage

Run the script followed by the hanime URL you want download:

```bash
python3 hanime_downloader.py <hanime_page_url>
```

Example

```
python3 hanime_downloader.py https://www.animesaturn.cx/anime/Orb-On-the-Movements-of-the-Earth
```

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the hanime URLs you want to download.

2. Run the main script via the command line:

```
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
