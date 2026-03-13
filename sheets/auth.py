import os
import json
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_credentials():
    # From env var (Railway)
    sa_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if sa_json:
        return service_account.Credentials.from_service_account_info(
            json.loads(sa_json), scopes=SCOPES
        )

    # From local file
    return service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES
    )
