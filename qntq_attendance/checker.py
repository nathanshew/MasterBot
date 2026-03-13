import os
from datetime import datetime
from .client import get_rows, _parse_date
from . import formatter


class Checker:
    def __init__(self, bot, chat_id, thread_id=None):
        self.bot = bot
        self.chat_id = chat_id
        self.thread_id = thread_id

    async def run(self, force=False):
        data = get_rows(os.getenv('ATTENDANCE_SHEET_ID'), os.getenv('ATTENDANCE_SHEET_NAME'))
        db = get_rows(os.getenv('OPEN_JIO_DATABASE_SHEET_ID'), os.getenv('OPEN_JIO_DATABASE_SHEET_NAME'), 'A:O') \
            if os.getenv('OPEN_JIO_DATABASE_SHEET_ID') else []

        col_indices, counts = self._get_columns(data, force=force)
        if not col_indices:
            return

        absent = self._find_absent(data, col_indices, db)
        special_care = self._find_special_care(data, col_indices, db, absent)
        absent = [m for m in absent if m not in {n for n, _ in special_care}]

        msg = self._build_message(col_indices, counts, absent, special_care, db)
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=msg,
            parse_mode='Markdown',
            **({"message_thread_id": self.thread_id} if self.thread_id else {})
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_columns(self, data, force=False):
        date_row = data[4] if len(data) > 4 else []
        today = datetime.now().date()

        cols = []
        for i in range(2, len(date_row)):
            d = _parse_date(date_row[i])
            if d and d.date() <= today:
                cols.append((i, d.date(), date_row[i].strip()))
        cols.sort(key=lambda x: x[1], reverse=True)
        cols = cols[:3]

        if not cols or (not force and today not in {c[1] for c in cols}):
            return [], {}

        col_indices = [(c[0], c[2]) for c in cols]
        counts = {
            idx: sum(1 for row in data[5:] if idx < len(row) and row[idx].strip())
            for idx, _ in col_indices
        }
        return col_indices, counts

    def _find_absent(self, data, col_indices, db):
        absent = []
        for row in data[5:]:
            name = row[1].strip() if len(row) > 1 else ''
            if not name:
                continue
            if all(not (row[idx].strip() if idx < len(row) else '') for idx, _ in col_indices):
                if not formatter._ignore_until(name, db):
                    absent.append(name)
        return absent

    def _find_special_care(self, data, col_indices, db, absent):
        special_care = []
        for row in data[5:]:
            name = row[1].strip() if len(row) > 1 else ''
            if not name or not formatter._is_special_care(name, db):
                continue
            attendance = [bool(row[idx].strip() if idx < len(row) else '') for idx, _ in col_indices]
            if any(attendance) or formatter._ignore_until(name, db):
                special_care.append((name, attendance))
        return special_care

    def _build_message(self, col_indices, counts, absent, special_care, db):
        if not absent and not special_care:
            return formatter.no_absences(col_indices, counts)

        return '\n'.join(filter(None, [
            formatter.header(col_indices, counts),
            formatter.absent_section(absent, db),
            formatter.special_care_section(special_care, db),
            formatter.birthdays_section(db),
        ]))
