from crewai import Agent, Task, Crew
from tools import one_page
from pydantic import BaseModel, Field
import pandas as pd

class Job(BaseModel):
    title: str
    location: str
    category: str
    job_id: str
    url: str
    
extractor = Agent(
    name="Extractor",
    role="Job Extraction Specialist",
    goal=("Receive raw job dictionaries, ensure each has "
          "title, location, category, job_id, and url."),
    backstory=("You are an expert data‑cleaner who validates and fixes "
               "scraped job records so they match a strict schema."),
    verbose=True,)
from tools.labcorp_tool import one_page
orchestrator = Agent(
    name="Orchestrator",
    role="Crawl Coordinator",
    goal="Crawl Labcorp, deduplicate jobs, save to CSV.",
    backstory="You orchestrate web crawling and delegate cleanup.",
    tools=[one_page],
    verbose=True,)


def build_crew(keyword: str) -> Crew:
    t1 = Task(
    description=("Determine how many Labcorp pages exist for the query "
                 f"“{keyword}”. Then, for each offset, call the "
                 "`one_page` tool to fetch raw job records. "
                 "Return a single list of all raw records."),
    agent=orchestrator)
    t2 = Task(
        description=("Clean the list to match Job schema exactly; "
                     "return an array of JSON."),
        agent=extractor,
        context=[t1],
        output_schema=Job)
    def save_action(jobs):
        df = pd.DataFrame([j.model_dump() for j in jobs])
        df.to_csv("labcorp_jobs.csv", index=False)
        return f"Saved {len(df)} rows to labcorp_jobs.csv"
    t3 = Task(
        description="Persist the cleaned jobs to CSV.",
        agent=orchestrator,
        context=[t2],
        action=save_action)
    return Crew(tasks=[t1, t2, t3])