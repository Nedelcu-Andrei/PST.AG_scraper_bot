# PST.AG_scraper_bot

## Requirements
- python 3.x.
  - Tested and developed on 3.8.0
- scrapy 2.8.0.
  - Tested and developed on 2.8.0

## Overview
- Scraper made only with Scrapy via concurrent requests.
- The scraper was done by reverse engineering the API to gather endpoints for the heavy JS rendered data, and the website for the data that was missing from endpoints or it required too many different requests to obtain it.
- Custom pipelines for xlsx and Json output files.
