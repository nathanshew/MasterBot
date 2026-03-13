from datetime import datetime
from googleapiclient.discovery import build
from sheets.auth import get_credentials

DATE_FORMATS = ['%d %b', '%d %b %Y', '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y', '%Y-%m-%d']


def _parse_date(s):
    for fmt in DATE_FORMATS:
        try:
            d = datetime.strptime(s.strip(), fmt)
            if '%Y' not in fmt and '%y' not in fmt:
                d = d.replace(year=datetime.now().year)
            return d
        except ValueError:
            continue
    return None


def _service():
    return build('sheets', 'v4', credentials=get_credentials())


def get_rows(sheet_id, sheet_name, range_='A:ZZ'):
    result = _service().spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"'{sheet_name}'!{range_}"
    ).execute()
    return result.get('values', [])
