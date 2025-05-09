# LabCorp Job Scraper

This Streamlit application uses AI to scrape and extract job listings from LabCorp's careers website. It allows users to search for specific job roles and download the results in CSV or Excel format.

## Features

- Search for jobs by keywords
- Extract job title, location, job ID, URL, and employment type
- Automatically handle pagination
- Download results as CSV or Excel
- Visual progress tracking
- Error handling and retries

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd labcorp-job-scraper
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install requirements:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file with the following content:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Or provide it in the app interface

5. Run the application:
   ```
   streamlit run main.py
   ```

6. Open your browser and navigate to `http://localhost:8501`

## How It Works

This application uses:

1. **Streamlit**: For the user interface
2. **LangChain**: For agent-based orchestration
3. **OpenAI LLM**: To intelligently parse HTML content
4. **RequestsWrapper**: To fetch web pages

The application works by:
1. Taking a search keyword from the user
2. Constructing a search URL for LabCorp's careers site
3. Fetching the search results page
4. Using AI to extract job details from the HTML
5. Following pagination links to gather all results
6. Presenting the data in a structured format
7. Enabling download options

## Notes

- This application respects website crawling etiquette with appropriate delays
- Error handling ensures resilience against temporary issues
- HTML parsing is done intelligently using LLMs rather than brittle selectors

## Limitations

- Changes to LabCorp's website structure might require updates
- Rate limits on API calls may affect performance
- Large result sets may take longer to process

## License
[MIT License]
