# imports
import json
import time
from typing import Callable, Optional
from langchain_openai import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
from langchain_community.tools import RequestsGetTool
from langchain.agents import initialize_agent, AgentType
from tools import ParsePageTool

def crawl_labcorp(start_url: str, progress_callback: Optional[Callable] = None):
    """
    Crawls the LabCorp careers website starting from the provided URL.
    
    Args:
        start_url: The starting URL for the search results
        progress_callback: Optional callback function to report progress
        
    Returns:
        List of job dictionaries with title, location, job_id, url, employment_type
    """
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    requests_wrapper = RequestsWrapper(headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    http_tool = RequestsGetTool(
        requests_wrapper=requests_wrapper,
        description="Make HTTP GET requests to fetch web pages",
        allow_dangerous_requests=True,)
    
    parse_tool = ParsePageTool(llm)
    
    tools = [http_tool, parse_tool]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
    )
    
    all_jobs = []
    url = start_url
    page_num = 1
    max_retries = 3
    
    while url:
        retry_count = 0
        success = False
        
        while not success and retry_count < max_retries:
            try:
                html = agent.run(f"requests_get url={url}")
                parse_result = agent.run(f"parse_page html={json.dumps(html)}")
                if not parse_result.strip().startswith('{'):
                    if '```json' in parse_result:
                        parse_result = parse_result.split('```json')[1].split('```')[0].strip()
                
                data = json.loads(parse_result)
                current_page_jobs = data.get("jobs", [])
                all_jobs.extend(current_page_jobs)
                if progress_callback:
                    progress_callback(page_num, len(all_jobs))
                next_page = data.get("next_page")
                if next_page and next_page.startswith("/"):
                    url = f"https://careers.labcorp.com{next_page}"
                else:
                    url = next_page
    
                page_num += 1
                success = True
                time.sleep(1)
                
            except Exception as e:
                retry_count += 1
                print(f"Error on page {page_num}: {str(e)}. Retrying {retry_count}/{max_retries}...")
                time.sleep(2)
                
                if retry_count >= max_retries:
                    print(f"Failed after {max_retries} retries on page {page_num}. Continuing to next page.")
                    url = None
    return all_jobs

if __name__ == "__main__":
    from pprint import pprint
    
    def print_progress(page, total):
        print(f"Processed page {page}. Found {total} jobs so far...")
    
    start = "https://careers.labcorp.com/global/en/search-results?keywords=QA%20automation%20testing"
    jobs = crawl_labcorp(start, print_progress)
    
    pprint(jobs[:3])
    print(f"Total jobs fetched: {len(jobs)}")