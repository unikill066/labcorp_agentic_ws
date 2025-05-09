# imports
from pydantic import BaseModel, Field, PrivateAttr
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json

parse_prompt = PromptTemplate(
    input_variables=["html"],
    template="""
You're given the HTML of a LabCorp search-results page.
Extract ALL job cards on that page, returning JSON with keys:
- jobs: a list of objects with fields title, location, job_id, url, employment_type
- next_page: href of the "next" link or null if none
- total_jobs: the total number of jobs found (from page header/metadata if available)

For job_id, extract only the numeric ID without any prefix.
For employment_type, determine if it's "Full-time", "Part-time", "Contract", etc. based on job description.
If employment_type is not explicitly mentioned, set it to "Not specified".

Return ONLY valid JSON.
HTML:
{html}
"""
)

class ParsePageTool(BaseTool):
    name: str = "parse_page"
    description: str = (
        "Parse LabCorp search-results HTML and return JSON with "
        "a list of jobs + next_page URL."
    )

    _llm: ChatOpenAI = PrivateAttr()
    _prompt: PromptTemplate = PrivateAttr()

    def __init__(self, llm: ChatOpenAI):
        super().__init__()
        object.__setattr__(self, "_llm", llm)
        object.__setattr__(self, "_prompt", parse_prompt)

    def _run(self, html: str) -> str:
        formatted_prompt = self._prompt.format(html=html)
        result = self._llm.invoke(formatted_prompt).content
        try:
            json_result = json.loads(result)
            return result
        except json.JSONDecodeError:
            import re
            json_pattern = r'```json\n(.*?)```'
            matches = re.search(json_pattern, result, re.DOTALL)
            if matches:
                json_text = matches.group(1)
                return json_text
            
            result = result.strip()
            if not result.startswith('{'):
                result = '{' + result.split('{', 1)[1]
            if not result.endswith('}'):
                result = result.rsplit('}', 1)[0] + '}'
            
            return result

    async def _arun(self, html: str) -> str:
        raise NotImplementedError("Async not supported")