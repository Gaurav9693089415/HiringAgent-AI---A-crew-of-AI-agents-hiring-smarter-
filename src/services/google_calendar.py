# src/services/google_calendar.py

from datetime import datetime, timedelta
import os
import pickle
import pytz
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Authenticate and return Google Calendar service credentials."""
    creds = None
    
    # Load existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Make sure credentials.json exists
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json file not found. Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_google_meet_event(candidate_email: str, preferred_time: str, recruiter_email: str):
    """
    Create a Google Calendar event with Google Meet integration.
    
    Args:
        candidate_email (str): Email of the candidate
        preferred_time (str): Time in format "YYYY-MM-DD HH:MM AM/PM"
        recruiter_email (str): Email of the recruiter
        
    Returns:
        str: Meeting link or error message
    """
    try:
        # Authenticate and build service
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)
        
        # Parse the preferred time
        tz = pytz.timezone("Asia/Kolkata")  # Adjust timezone as needed
        try:
            start_time = datetime.strptime(preferred_time, "%Y-%m-%d %I:%M %p")
        except ValueError:
            # Try alternative format
            try:
                start_time = datetime.strptime(preferred_time, "%Y-%m-%d %H:%M")
            except ValueError:
                return "Error: Invalid time format. Expected 'YYYY-MM-DD HH:MM AM/PM'"
        
        start_time = tz.localize(start_time)
        end_time = start_time + timedelta(hours=1)  # 1-hour meeting
        
        # Create the event
        event = {
            'summary': 'Job Interview',
            'description': f'Interview with candidate {candidate_email}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [
                {'email': candidate_email},
                {'email': recruiter_email}
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
        }
        
        # Insert the event
        event_result = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all'  # Send invitations to all attendees
        ).execute()
        
        # Extract the Google Meet link
        meet_link = event_result.get('hangoutLink')
        event_id = event_result.get('id')
        
        if meet_link:
            return meet_link
        else:
            return f"Event created successfully (ID: {event_id}) but no Google Meet link was generated. Please check your Google Calendar."
            
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error creating Google Meet event: {str(e)}"

def list_upcoming_events(max_results=10):
    """List upcoming events from Google Calendar."""
    try:
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)
        
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
    except Exception as e:
        return f"Error fetching events: {str(e)}"