# src/resume_processor.py

import os
from crewai import Crew, Process, Task
from src.agents.agents import (
    web_scraper_agent,
    embedding_matcher_agent,
    llm_analyst_agent,
    decision_maker_agent,
    interview_scheduler_agent
)
from config.settings import MINIMUM_PASSING_SCORE


def run_recruitment_workflow(resume_file_path: str, job_url: str, preferred_time: str = None, candidate_email: str = None):
    """
    Runs the full recruitment workflow.
    Screening phase runs without requiring preferred_time or candidate_email.
    Scheduling phase runs only if both preferred_time and candidate_email are provided.
    """
    print("--- Starting the Hybrid Recruitment Workflow ---")

    # --- Task 1: Scrape the job description ---
    scrape_job_description_task = Task(
        description=(
            f"Use the Web Scraper tool to fetch the job description from the URL: '{job_url}'. "
            "Return the clean text of the job description."
        ),
        agent=web_scraper_agent,
        expected_output="The full text content of the job description from the given URL."
    )

    # --- Task 2: Initial filtering with embeddings and email extraction ---
    embedding_filter_task = Task(
        description=(
            f"First, use the Resume Parser tool to extract the text and email from the resume file at '{resume_file_path}'. "
            f"Then, use the Embedding Matcher tool to perform an initial relevance check "
            f"on the extracted resume text against the job description scraped earlier. "
            "Return a JSON object containing both the candidate's email address and the numerical similarity score. "
            "Format: {'email': 'candidate@email.com', 'similarity_score': 85.5}"
        ),
        agent=embedding_matcher_agent,
        expected_output="A JSON object containing 'email' (string) and 'similarity_score' (float)."
    )

    # --- Task 3: Detailed LLM verification ---
    llm_verification_task = Task(
        description=(
            "The resume passed the initial filter. Perform a deep, contextual "
            "analysis of the resume against the job description. Generate a final "
            f"relevance score out of 100 and a detailed summary. If the score is "
            f"below {MINIMUM_PASSING_SCORE}, stop here."
        ),
        agent=llm_analyst_agent,
        expected_output="A JSON object containing 'score' (integer) and 'summary' (string)."
    )

    # --- Task 4: Make a hiring decision ---
    decision_task = Task(
        description=(
            f"Review the final score and summary from the LLM Analyst. "
            f"Based on the company policy (score >= {MINIMUM_PASSING_SCORE}), "
            "make a final decision. Output either 'Proceed with interview' or 'Reject'."
        ),
        agent=decision_maker_agent,
        expected_output="A string: 'Proceed with interview' or 'Reject'."
    )

    # --- Task 5: Schedule interview (ONLY if details provided) ---
    tasks = [scrape_job_description_task, embedding_filter_task, llm_verification_task, decision_task]

    if preferred_time and candidate_email:
        schedule_interview_task = Task(
            description=(
                "If the previous decision was 'Proceed with interview', "
                "use the Interview Scheduler tool to create a Google Meet. "
                f"The candidate's email is '{candidate_email}' and the preferred time is '{preferred_time}'. "
                "Output a confirmation message with the meeting link."
            ),
            agent=interview_scheduler_agent,
            expected_output="A confirmation string containing the meeting link and details."
        )
        tasks.append(schedule_interview_task)
    else:
        print("⚠ Skipping scheduling task because preferred_time or candidate_email was not provided.")

    # --- Create and run the crew ---
    recruitment_crew = Crew(
        agents=[
            web_scraper_agent,
            embedding_matcher_agent,
            llm_analyst_agent,
            decision_maker_agent,
            interview_scheduler_agent
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    result = recruitment_crew.kickoff(inputs={
        'resume_file_path': resume_file_path,
        'job_url': job_url,
        'preferred_time': preferred_time or "",
        'candidate_email': candidate_email or ""
    })

    print("--- Workflow Finished ---")
    print(result)
    return result