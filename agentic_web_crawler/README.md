# Labcorp Job Crawler

A specialized web crawler built with CrewAI that extracts job listings from Labcorp's career website.

## Overview

This project uses an agent-based approach to:
1. Crawl Labcorp's career search pages for job listings
2. Extract job information (title, location, category, job ID, URL)
3. Clean and validate the data
4. Export the results to a CSV file

## Project Structure

```
├── run_scraper.py
├── crew_config.py
├── tools/
│   ├── __init__.py
│   └── labcorp_tool.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- CrewAI
- Playwright
- BeautifulSoup4
- Pandas
- Pydantic

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

Run the scraper with a search keyword:

```bash
python run_scraper.py "qa automation"
```

Or run it without arguments to be prompted for a keyword:

```bash
python run_scraper.py
```

## How It Works

The crawler utilizes CrewAI's agent framework to orchestrate the job extraction process:

1. **Orchestrator Agent** - Coordinates the overall crawling process:
   - Determines how many pages of results exist
   - Calls the `one_page` tool for each page offset
   - Saves the final processed data to CSV

2. **Extractor Agent** - Cleans and validates job data:
   - Ensures all required fields are present
   - Formats data according to the Job schema
   - Returns validated job listings

## Output

The crawler will generate a file named `labcorp_jobs.csv` containing the following fields:
- `title` - Job title
- `location` - Job location
- `category` - Job category
- `job_id` - Unique job identifier
- `url` - Direct link to the job posting

## Customization

To modify the crawler for different websites or data structures:
1. Create a new tool in the `tools/` directory
2. Adjust the `Job` schema in `crew_config.py`
3. Update the agent tasks as needed

## License
[MIT License]