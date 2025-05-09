from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import urllib.parse, math

RESULTS_PER_PAGE = 20
SELECTOR = '[data-ph-at-id="job-link"]'

def one_page(keyword: str, offset: int) -> List[Dict]:
    """Return a list of job‑dicts from one Labcorp page."""
    url = ("https://careers.labcorp.com/global/en/search-results"
           f"?keywords={urllib.parse.quote_plus(keyword)}&from={offset}&s=1")

    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()

    soup = BeautifulSoup(html, "lxml")
    jobs = []
    for li in soup.select(SELECTOR):
        a = li.find("a", {"data-ph-at-id": "job-link"})
        jobs.append({
            "title": a.get_text(strip=True),
            "url":   "https://careers.labcorp.com" + a["href"],
            "location": (loc := li.select_one('[data-ph-at-id="job-location"]')
                         and loc.get_text(strip=True)) or "",
            "category": (cat := li.select_one('[data-ph-at-id="job-category"]')
                         and cat.get_text(strip=True)) or "",
            "job_id": li.get("data-job-id") or a["href"].split("-")[-1]})
    return jobs