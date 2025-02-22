from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json

CONFIG = {
    'CLIENT_SECRETS_FILE': os.getenv('CLIENT_SECRETS_FILE', 'config/client_secret.json'),
    'TOKEN_FILE': os.getenv('TOKEN_FILE', 'config/token.json')
}

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/calendar.events'
]


def authenticate():
    creds = None

    if os.path.exists(CONFIG['TOKEN_FILE']):
        with open(CONFIG['TOKEN_FILE'], 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CONFIG['CLIENT_SECRETS_FILE'], SCOPES)
            creds = flow.run_local_server(port=0)

        with open(CONFIG['TOKEN_FILE'], 'w') as token:
            token.write(creds.to_json())

    return creds