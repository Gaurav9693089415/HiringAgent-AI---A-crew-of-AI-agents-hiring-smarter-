import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Defaults for job description, resume, and interview time
DEFAULT_JOB_DESCRIPTION = "We are looking for Gen AI engineer with expertise in Python and machine learning."
DEFAULT_RESUME_PATH = "data/resumes/sample_resume.pdf"
DEFAULT_INTERVIEW_TIME = "2025-08-12 03:00 PM"  # <--- Added to fix error

# Scoring thresholds
MINIMUM_PASSING_SCORE = 80  # Final decision score for interview
DEFAULT_EMBEDDING_THRESHOLD = 70.0  # Initial similarity score to pass to next stage
