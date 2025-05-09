# config.py

BASE_URL = "https://careers.labcorp.com/global/en/search-results?keywords=CHAR_STRING&from=PAGE_NO&s=1"
CSS_SELECTOR = '[data-ph-at-id="jobs-list-item"]'
# CSS_SELECTOR = "li.jobs-list-item"  # CSS_SELECTOR = "[class^='jobs-list-item']"
REQUIRED_KEYS = [
    "title",
    "location",
    "role",
    "job_id",
    "url",
]