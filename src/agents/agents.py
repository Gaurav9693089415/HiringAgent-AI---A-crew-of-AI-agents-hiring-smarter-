# src/agents/agents.py

import os
import requests
import re
import json
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
# We'll use this library to handle PDFs, need to install it first.
import fitz
# For embeddings, you'll need a library like sentence-transformers.
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer, util
from src.services.google_calendar import create_google_meet_event


# --- Custom Tools ---

class ResumeParserTool(BaseTool):
    name: str = "Resume Parser"
    description: str = "Parses a PDF file and returns its text content and email address."

    def _run(self, file_path: str) -> dict:
        """Reads a PDF file and extracts all text and the first email address found."""
        try:
            with fitz.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            
            # Use a regular expression to find the first email address
            # This regex is more robust and can handle various formats
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            email = email_match.group(0) if email_match else "Email not found"
            
            return {"text": text, "email": email}
        except Exception as e:
            return {"text": "", "email": "Error parsing PDF file."}


class WebScraperTool(BaseTool):
    name: str = "Web Scraper"
    description: str = "Scrapes the text content from a given URL to extract the job description."

    def _run(self, url: str) -> str:
        """Scrapes the text from a web page."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()
            # Clean up the text by removing extra whitespace and newlines
            clean_text = ' '.join(text_content.split())
            return clean_text
        except Exception as e:
            return f"Error scraping URL: {e}"


class EmbeddingMatcherTool(BaseTool):
    name: str = "Embedding Matcher"
    description: str = (
        "Compares a resume text with a job description using sentence embeddings "
        "to get a quick similarity score. This is used for initial filtering."
    )

    def _run(self, resume_text: str, job_description: str) -> float:
        """Calculates the similarity score between two texts."""
        model = SentenceTransformer('all-MiniLM-L6-v2')
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        score = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
        return score * 100


class InterviewSchedulerTool(BaseTool):
    name: str = "Interview Scheduler"
    description: str = "Schedules a Google Meet interview and sends an invitation to the candidate."

    def _run(self, candidate_email: str, preferred_time: str) -> str:
        """Schedules a Google Meet event via the Google Calendar API."""
        try:
            from src.services.google_calendar import create_google_meet_event
            
            recruiter_email = "gauravkumar00514@gmail.com"  # Replace with your email
            
            # Create the Google Meet event
            result = create_google_meet_event(
                candidate_email=candidate_email,
                preferred_time=preferred_time,
                recruiter_email=recruiter_email
            )
            
            # Check if it's an error message
            if result.startswith("Error"):
                return result
            elif result.startswith("Event created successfully"):
                return result
            elif result.startswith("https://meet.google.com/"):
                # It's a meeting link
                return (
                    f"Interview scheduled successfully for {candidate_email} on {preferred_time}. "
                    f"Google Meet link: {result} "
                    f"Invitation has been sent to all attendees."
                )
            else:
                return f"Interview scheduled but unexpected response: {result}"
                
        except ImportError:
            return "Error: Google Calendar service not available. Please check your installation."
        except Exception as e:
            return f"Error in InterviewSchedulerTool: {str(e)}"


# --- Agent Definitions ---

# New Web Scraper Agent to fetch job descriptions
web_scraper_agent = Agent(
    role="Web Scraper",
    goal="Fetch a job description from a provided URL.",
    backstory=(
        "You are an expert web scraper, capable of extracting clean, readable text "
        "from any public web page. Your goal is to get a job description from a URL "
        "so other agents can use it."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[WebScraperTool()]
)

# Updated Embedding Matcher Agent to handle email extraction properly
embedding_matcher_agent = Agent(
    role="Embedding Matcher",
    goal="Parse the resume, extract email, and quickly filter resumes using embeddings to find a similarity score.",
    backstory=(
        "You are an ultra-fast AI assistant focused on the initial screening of resumes. "
        "You first extract the candidate's email from the resume, then use a sophisticated embedding model "
        "to compare the resume against a job description and provide a quick, numerical score. "
        "You must return both the email address and similarity score in a structured format."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[ResumeParserTool(), EmbeddingMatcherTool()]
)

# Existing LLM-based Resume Analyst Agent
llm_analyst_agent = Agent(
    role="LLM Analyst",
    goal="Perform a deep, contextual analysis of a resume that has passed the initial filter. "
         "Provide a detailed, final score and a human-readable explanation.",
    backstory=(
        "You are a professional hiring manager with a keen eye for detail. "
        "You are an expert at providing a nuanced, objective score and analysis. "
        "Your task is to take a filtered resume and give a final, high-quality review."
    ),
    verbose=True,
    allow_delegation=False
)

# Existing Hiring Decision Maker Agent
decision_maker_agent = Agent(
    role="Hiring Decision Maker",
    goal="Evaluate the final LLM-based resume score and decide whether to proceed with an interview or not.",
    backstory=(
        "You are the final decision maker in the hiring process. You follow a strict rule: "
        "only candidates with a score of 80% or higher are considered for an interview."
    ),
    verbose=True,
    allow_delegation=False
)

# Existing Interview Scheduler Agent
interview_scheduler_agent = Agent(
    role="Interview Scheduler",
    goal="Schedule a Google Meet interview with a qualified candidate.",
    backstory=(
        "You are an administrative assistant specializing in scheduling. You can "
        "create and send Google Meet invitations to candidates for a chosen time slot."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[InterviewSchedulerTool()]
)