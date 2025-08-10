# src/web_app.py

import streamlit as st
import os
import sys
import datetime
import json
import hashlib
from werkzeug.utils import secure_filename

# Ensure absolute imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.resume_processor import run_recruitment_workflow

# --- App Configuration ---
st.set_page_config(page_title="Agentic AI Resume Checker", layout="centered")

# --- Session State Initialization ---
if 'processed_resumes' not in st.session_state:
    st.session_state.processed_resumes = {}
if 'show_calendar' not in st.session_state:
    st.session_state.show_calendar = False
if 'selected_candidate' not in st.session_state:
    st.session_state.selected_candidate = None
if 'job_url' not in st.session_state:
    st.session_state.job_url = ""
if 'cache' not in st.session_state:
    st.session_state.cache = {}

# --- UI Elements ---
st.title("Agentic AI Resume Checker")
st.markdown("Upload multiple resumes and a job posting URL to get a detailed hiring recommendation.")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

job_url = st.text_input(
    "Job Description URL",
    help="Enter a URL to a job posting (e.g., from LinkedIn or a company website)."
)
if job_url:
    st.session_state.job_url = job_url

# --- Workflow Trigger ---
if st.button("Check Resumes"):
    if uploaded_files and st.session_state.job_url:
        st.session_state.processed_resumes = {}
        st.session_state.show_calendar = False
        st.session_state.selected_candidate = None

        UPLOAD_FOLDER = "data/resumes"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.name)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            file_hash = hashlib.sha256(uploaded_file.getbuffer()).hexdigest()
            cache_key = f"{file_hash}-{st.session_state.job_url}"

            if cache_key in st.session_state.cache:
                st.info(f"Using cached result for {filename}...")
                st.session_state.processed_resumes[filename] = st.session_state.cache[cache_key]
                continue

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                with st.spinner(f"Processing resume: {filename}..."):
                    crew_output = run_recruitment_workflow(
                        resume_file_path=file_path,
                        job_url=st.session_state.job_url,
                        preferred_time="",
                        candidate_email=""
                    )

                final_decision = "Could not parse final decision."
                llm_score = 0
                llm_summary = "Could not parse LLM summary."
                candidate_email = "Email not found"

                # Parse the task outputs
                for task_output in crew_output.tasks_output:
                    if task_output.agent == "Hiring Decision Maker":
                        final_decision = task_output.raw.strip()
                    elif task_output.agent == "LLM Analyst":
                        llm_data_str = task_output.raw.strip()
                        if llm_data_str.startswith('{') and llm_data_str.endswith('}'):
                            llm_data = json.loads(llm_data_str)
                            llm_score = llm_data.get("score", 0)
                            llm_summary = llm_data.get("summary", "Summary not found.")
                    elif task_output.agent == "Embedding Matcher":
                        # The embedding matcher should return the parsed resume data including email
                        if isinstance(task_output.raw, dict):
                            candidate_email = task_output.raw.get("email", "Email not found")
                        elif isinstance(task_output.raw, str):
                            # If it's a string, try to parse it as JSON
                            try:
                                parsed_data = json.loads(task_output.raw)
                                candidate_email = parsed_data.get("email", "Email not found")
                            except json.JSONDecodeError:
                                # If it's not JSON, it might be just the score, so we need to get email differently
                                # We'll need to extract email from the raw crew output or task context
                                pass

                # If we still don't have email, try to extract it from the crew output directly
                if candidate_email == "Email not found":
                    try:
                        # Look for email in any task output that might contain it
                        for task_output in crew_output.tasks_output:
                            if hasattr(task_output, 'raw') and isinstance(task_output.raw, str):
                                import re
                                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', task_output.raw)
                                if email_match:
                                    candidate_email = email_match.group(0)
                                    break
                    except:
                        pass

                st.session_state.processed_resumes[filename] = {
                    "decision": final_decision,
                    "score": llm_score,
                    "summary": llm_summary,
                    "email": candidate_email,
                    "file_path": file_path
                }
                st.session_state.cache[cache_key] = st.session_state.processed_resumes[filename]

            except Exception as e:
                st.error(f"Error processing {filename}: {e}")

        for filename, data in st.session_state.processed_resumes.items():
            if "Proceed with interview" in data["decision"]:
                st.session_state.show_calendar = True
                break
    else:
        st.warning("Please upload at least one resume and provide a job URL.")

# --- Display Results ---
if st.session_state.processed_resumes:
    st.markdown("---")
    st.subheader("Resume Screening Results")

    interview_candidates = []

    for filename, data in st.session_state.processed_resumes.items():
        st.markdown(f"**Resume:** {filename}")
        st.write(f"**Score:** {data['score']}/100")
        st.write(f"**Decision:** {data['decision']}")
        st.write(f"**Email:** {data['email']}")  # Show extracted email
        with st.expander("Show LLM Summary"):
            st.write(data['summary'])
        st.markdown("---")

        if "Proceed with interview" in data["decision"]:
            interview_candidates.append(filename)

    if st.session_state.show_calendar:
        st.subheader("Schedule an Interview")

        selected_candidate = st.selectbox(
            "Select candidate:",
            options=interview_candidates,
            key="candidate_select"
        )

        if selected_candidate:
            email_to_use = st.session_state.processed_resumes.get(selected_candidate, {}).get("email", "")
            
            if email_to_use and email_to_use != "Email not found":
                st.success(f"✅ Email automatically extracted: **{email_to_use}**")
                candidate_email = email_to_use
                
                # Show the email but make it editable in case it's wrong
                candidate_email = st.text_input(
                    "Candidate's Email Address:",
                    value=email_to_use,
                    help="Email was automatically extracted from resume. You can edit if needed."
                )
            else:
                st.warning("⚠️ Email could not be extracted from resume. Please enter manually.")
                candidate_email = st.text_input(
                    "Candidate's Email Address (Required):",
                    key="candidate_email_input",
                    help="Email extraction failed. Please enter the candidate's email manually."
                )

            selected_date = st.date_input("Choose a date:", datetime.date.today())
            selected_time = st.time_input("Choose a time:", datetime.time(10, 0))

            if selected_candidate and candidate_email and candidate_email.strip() != "" and st.button("Schedule Meeting"):
                preferred_time_str = f"{selected_date.strftime('%Y-%m-%d')} {selected_time.strftime('%I:%M %p')}"

                file_path_for_scheduling = st.session_state.processed_resumes[selected_candidate]["file_path"]

                with st.spinner(f"Scheduling interview for {selected_candidate}..."):
                    try:
                        crew_output_scheduling = run_recruitment_workflow(
                            resume_file_path=file_path_for_scheduling,
                            job_url=st.session_state.job_url,
                            preferred_time=preferred_time_str,
                            candidate_email=candidate_email
                        )

                        meeting_link = None
                        event_id = None
                        scheduling_result = None
                        
                        for task_output in crew_output_scheduling.tasks_output:
                            if task_output.agent == "Interview Scheduler":
                                scheduling_result = task_output.raw.strip()
                                # Extract meeting link from the response
                                import re
                                link_match = re.search(r'https://meet\.google\.com/[a-zA-Z0-9-]+', scheduling_result)
                                if link_match:
                                    meeting_link = link_match.group(0)
                                
                                # Extract event ID if present
                                event_match = re.search(r'Event ID: ([a-zA-Z0-9_-]+)', scheduling_result)
                                if event_match:
                                    event_id = event_match.group(1)

                        if meeting_link:
                            st.success(f" Interview scheduled successfully!")
                            st.success(f" Invitation sent to: {candidate_email}")
                            st.success(f" Meeting Link: [Join Meeting]({meeting_link})")
                            if event_id:
                                st.info(f" Calendar Event ID: {event_id}")
                        elif "scheduled successfully" in scheduling_result.lower():
                            st.success(f" Interview scheduled successfully!")
                            st.success(f" Invitation sent to: {candidate_email}")
                            st.warning(" Meeting link not found in response, but event was created. Please check your calendar.")
                            st.info(f"Scheduler Response: {scheduling_result}")
                        else:
                            st.error(f" Failed to schedule interview: {scheduling_result}")

                    except Exception as schedule_error:
                        st.error(f"Error scheduling interview: {schedule_error}")
            elif selected_candidate and not candidate_email.strip():
                st.warning("Please enter a valid email address to schedule the interview.")