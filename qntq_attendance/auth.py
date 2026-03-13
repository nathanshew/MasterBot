import os
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_credentials():
    # Service account via env var (Railway)
    sa_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if sa_json:
        return service_account.Credentials.from_service_account_info(
            json.loads(sa_json), scopes=SCOPES
        )

    # Detect credentials.json type
    if os.path.exists('credentials.json'):
        with open('credentials.json') as f:
            info = json.load(f)

        # Service account key file
        if info.get('type') == 'service_account':
            return service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES
            )

    # OAuth flow (local dev with OAuth Desktop app credentials)
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as f:
                f.write(creds.to_json())
        return creds

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as f:
        f.write(creds.to_json())
    return creds
