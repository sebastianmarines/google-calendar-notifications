from pathlib import Path

from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google_calendar_notifications.settings import CREDENTIALS, SCOPES
from google_auth_oauthlib.flow import InstalledAppFlow

if __name__ == "__main__":
    home = Path.home()
    app_directory = home / ".google-calendar-notifications"
    if not app_directory.exists():
        Path.mkdir(app_directory)

    creds: Optional[Credentials] = None

    creds_file = app_directory / "token.json"

    if creds_file.exists():
        creds = Credentials.from_authorized_user_file(creds_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(creds_file, 'w') as token:
            token.write(creds.to_json())
