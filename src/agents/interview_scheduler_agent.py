# src/agents/interview_scheduler_agent.py
from datetime import datetime, timedelta
import os
import pickle
import pytz

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

class RealInterviewScheduler:
    def __init__(self):  # Fixed the constructor name
        self.creds = None
        self.authenticate()

    def authenticate(self):
        """Authenticate and store the Google Calendar API credentials."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def schedule(self, candidate_email: str, preferred_time: str, job_title: str = "Position"):
        """Create a Google Calendar event with a Meet link."""
        try:
            service = build('calendar', 'v3', credentials=self.creds)

            # Convert preferred_time string to datetime
            tz = pytz.timezone("Asia/Kolkata")
            start_time = datetime.strptime(preferred_time, "%Y-%m-%d %I:%M %p")
            start_time = tz.localize(start_time)
            end_time = start_time + timedelta(hours=1)

            event = {
                'summary': f'Interview for {job_title}',
                'description': f'Interview scheduled for {job_title} position with {candidate_email}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [
                    {'email': candidate_email}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{int(datetime.now().timestamp())}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                }
            }

            event_result = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            return {
                "status": "success",
                "meet_link": event_result.get("hangoutLink"),
                "event_id": event_result.get("id")
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to schedule interview: {str(e)}"
            }

# Create a global instance
real_interview_scheduler = RealInterviewScheduler()