import asyncio
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv
from config import BASE_URL, CSS_SELECTOR, REQUIRED_KEYS
from utils.data_utils import save_jobs_to_csv
from utils.scraper_utils import fetch_and_process_page, get_browser_config, get_llm_strategy

load_dotenv()

async def crawl_jobs():
    """
    Main function to crawl job data from the website.
    """
    # Initialize configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "job_crawl_session"

    # Initialize state variables
    page_number = 20
    all_jobs = []
    seen_names = set()

    char_string = input("Enter the job you are searching for: ")

    # Start the web crawler context
    # https://docs.crawl4ai.com/api/async-webcrawler/#asyncwebcrawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            print(BASE_URL.replace("CHAR_STRING", "%20".join(char_string.split())).replace("PAGE_NO", str(page_number)))
            jobs, no_results_found = await fetch_and_process_page(
                crawler,
                page_number,
                BASE_URL.replace("CHAR_STRING", "%20".join(char_string.split())).replace("PAGE_NO", str(page_number)),
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_names,
            )

            if no_results_found:
                print("No more jobs found. Ending crawl.")
                break  # Stop crawling when "No Results Found" message appears

            if not jobs:
                print(f"No jobs extracted from page {page_number}.")
                break  # Stop if no jobs are extracted

            # Add the jobs from this page to the total list
            all_jobs.extend(jobs)
            page_number = page_number - 1  # Move to the next page

            # Pause between requests to be polite and avoid rate limits
            await asyncio.sleep(2)  # Adjust sleep time as needed

    # Save the collected jobs to a CSV file
    if all_jobs:
        save_jobs_to_csv(all_jobs, "complete_jobs.csv")
        print(f"Saved {len(all_jobs)} jobs to 'complete_jobs.csv'.")
    else:
        print("No jobs were found during the crawl.")

    # Display usage statistics for the LLM strategy
    llm_strategy.show_usage()


async def main():
    """
    Entry point of the script.
    """
    await crawl_jobs()


if __name__ == "__main__":
    asyncio.run(main())
