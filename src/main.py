import os
from src.resume_processor import run_recruitment_workflow
from config.settings import DEFAULT_RESUME_PATH, DEFAULT_JOB_DESCRIPTION

if __name__ == '__main__':
    resumes_dir = os.path.dirname(DEFAULT_RESUME_PATH)
    if not os.path.exists(resumes_dir):
        os.makedirs(resumes_dir)

    print("--- Starting the Agentic Resume Checker Application ---")
    
    run_recruitment_workflow(
        resume_file_path=DEFAULT_RESUME_PATH,
        job_description=DEFAULT_JOB_DESCRIPTION
    )
    
    print("--- Application finished successfully ---")
