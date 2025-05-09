# imports
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from agent_runner import crawl_labcorp

load_dotenv()

st.set_page_config(
    page_title="LabCorp Job Scraper",
    page_icon="💼",
    layout="wide"
)

st.title("LabCorp Job Scraper (AI-powered)")
st.markdown("""
This app uses AI to extract job listings from LabCorp's careers page.
Enter keywords below to search for relevant jobs.
""")
keywords = st.text_input("Enter search keywords", "QA automation testing")
if not os.getenv("OPENAI_API_KEY"):
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.warning("Please enter your OpenAI API key to continue.")
        st.stop()

if st.button("Search Jobs"):
    base = "https://careers.labcorp.com/global/en/search-results"
    start_url = f"{base}?keywords={keywords.replace(' ', '%20')}"
    progress_bar = st.progress(0)
    status_text = st.empty()
    col1, col2 = st.columns(2)
    
    with st.spinner("Crawling & parsing job listings..."):
        status_text.text("Initializing search...")
        
        def progress_callback(current_page, total_jobs):
            progress_value = min(current_page * 0.1, 0.95)
            progress_bar.progress(progress_value)
            status_text.text(f"Processed page {current_page}. Found {total_jobs} jobs so far...")
            
        try:
            jobs = crawl_labcorp(start_url, progress_callback)
            progress_bar.progress(1.0)
            status_text.text("Search complete!")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

    if not jobs:
        st.warning("No jobs found matching your search criteria. Try different keywords.")
    else:
        df = pd.DataFrame(jobs)
        with col1:
            st.metric("Total Jobs Found", len(df))
        with col2:
            locations = df['location'].value_counts().to_dict()
            top_location = max(locations.items(), key=lambda x: x[1]) if locations else ('N/A', 0)
            st.metric("Top Location", f"{top_location[0]} ({top_location[1]} jobs)")
        st.subheader("Search Results")
        st.dataframe(df,
            column_config={
                "url": st.column_config.LinkColumn("Job Link"),
                "title": "Job Title",
                "location": "Location",
                "job_id": "Job ID",
                "employment_type": "Employment Type"},hide_index=True)
        
        csv = df.to_csv(index=False)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download as CSV",
                csv,
                file_name=f"labcorp_jobs_{keywords.replace(' ','_')}.csv",
                mime="text/csv",
                key="csv-download")
        
        with col2:
            buffer = df.to_excel(index=False, engine='openpyxl')
            st.download_button(
                "Download as Excel",
                buffer,
                file_name=f"labcorp_jobs_{keywords.replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="excel-download")