# Steam Apps Scrapy Project

Scrapy project to scrape steam apps and save html in warc format, extract apps data and media.

Coded and tested on python version 3.11.2

## Installation

Create and environment and run:

`pip install -r requirements.py`

If you're on windows and have problems running the spider, run:

`pip install python-magic-bin`

## How to run:

All commands described below must be run in the project's root

### 1. Create jobs database

⚠️ Make sure to run it only once before starting the scraping job because purges the database, loosing all jobs state
data

The database is already provided but if you need to re-create it with up to date steams apps data, just
replace the `steamcmd_appid.json` file and run:

`python steam_scraping/create_json_db.py`

Jobs have the following fields:

1. appid
2. name
3. status
    - pending (default)
    - partial some media content failed to be downloaded/saved
    - complete
    - failed
4. err_msg in case of partial or failed

### 2. Start scraping

`scrapy crawl apps`

You can choose what jobs to scrape by passing status argument to spider. pending (default) | partial | complete | failed

`scrapy crawl apps -a status=failed`

## Storage

Html is written to warc file only if response is in 200 range

Extracted app data have these fields:

- app_id, game_title, publisher, developer, publish_date, tags, images_path, videos_path

Warc files are saved to `files/warc-files`. Media content to `files/media/<app_id>`

### Export format

In `settings.py` you can modify everything related to the file in which the extracted data is stored:

```py
FEEDS = {'data.jsonl': {  # name of file
    'format': 'jsonl',
    'encoding': 'utf8',
    'store_empty': True,
    'fields': ['app_id', 'game_title', 'publisher', 'developer', 'publish_date', 'tags', 'images_path', 'videos_path'],
    'indent': 4,
    # whether overwrite or append
    'overwrite': False
}}
```