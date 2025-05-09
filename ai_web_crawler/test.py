import asyncio, csv, math, urllib.parse, re, itertools
from typing import List, Dict

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

RESULTS_PER_PAGE = 20
SELECTOR_CARD    = '[data-ph-at-id="job-link"]'   # every job <li> has this

def build_url(query: str, offset: int) -> str:
    encoded = urllib.parse.quote_plus(query)
    return (f"https://careers.labcorp.com/global/en/"
            f"search-results?keywords={encoded}&from={offset}&s=1")

def parse_cards(html: str) -> List[Dict]:
    """Extract fields from the HTML of one results page."""
    soup  = BeautifulSoup(html, "lxml")
    cards = soup.select(SELECTOR_CARD)
    jobs  = []
    for li in cards:
        a_tag = li.find("a", {"data-ph-at-id": "job-link"})
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        url   = "https://careers.labcorp.com" + a_tag["href"]

        # the site embeds these bits in spans; fall back to empty string
        location  = li.select_one('[data-ph-at-id="job-location"]')
        category  = li.select_one('[data-ph-at-id="job-category"]')
        job_id    = li.get("data-job-id") or url.split("-")[-1]

        jobs.append(
            dict(
                title     = title,
                location  = location.get_text(strip=True) if location else "",
                category  = category.get_text(strip=True) if category else "",
                job_id    = job_id,
                url       = url,
            )
        )
    return jobs

async def scrape(keyword: str) -> List[Dict]:
    jobs: List[Dict] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page    = await browser.new_page()

        # ── first page ────────────────────────────────────────────────────────
        offset = 0
        url    = build_url(keyword, offset)
        await page.goto(url, wait_until="networkidle")
        html   = await page.content()
        jobs.extend(parse_cards(html))

        # ── figure out how many pages we actually have ───────────────────────
        # Look for “Showing 262 results” anywhere in the HTML
        match  = re.search(r"Showing\s+(\d+)\s+results", html, re.I)
        if match:
            total_results = int(match.group(1))
            pages = math.ceil(total_results / RESULTS_PER_PAGE)
        else:
            # Fallback: we don't know the total → we'll iterate until empty
            pages = math.inf

        print(f"Initial page returned {len(jobs)} jobs. Total pages: {pages}")

        # ── subsequent pages ─────────────────────────────────────────────────
        for page_idx in itertools.count(1):          # 1,2,3,… until break
            if page_idx >= pages:
                break

            offset = page_idx * RESULTS_PER_PAGE
            url    = build_url(keyword, offset)
            print(f"Fetching offset {offset}")

            await page.goto(url, wait_until="networkidle")
            html = await page.content()
            page_jobs = parse_cards(html)

            if not page_jobs:        # empty page ⇒ we're done
                break

            jobs.extend(page_jobs)
            await asyncio.sleep(1.5)

        await browser.close()
    return jobs

def save_csv(rows: List[Dict], filename: str) -> None:
    if not rows:
        print("No jobs captured.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {filename}")

if __name__ == "__main__":
    kw = input("Enter job keyword(s): ").strip()
    if not kw:
        print("Keyword required.")
        exit(1)

    data = asyncio.run(scrape(kw))
    save_csv(data, "labcorp_jobs.csv")
