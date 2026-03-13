from datetime import datetime


def fmt(minutes):
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h {m}min"
    return f"{h}h" if h else f"{m}min"


def parse_duration(s):
    """'2h' → 120, '30min' → 30, '1.5h' → 90"""
    s = s.strip().lower()
    if s.endswith('h'):
        return int(float(s[:-1]) * 60)
    if s.endswith('min'):
        return int(s[:-3])
    if s.endswith('m'):
        return int(s[:-1])
    raise ValueError(f"Can't parse duration: {s}. Use e.g. 2h, 30min, 1.5h")


def parse_date(s):
    """'13/03' or '13/03/26' or '2026-03-13' → date"""
    for fmt_ in ('%d/%m/%Y', '%d/%m/%y', '%d/%m', '%Y-%m-%d'):
        try:
            d = datetime.strptime(s.strip(), fmt_)
            if fmt_ == '%d/%m':
                d = d.replace(year=datetime.now().year)
            return d.date()
        except ValueError:
            continue
    raise ValueError(f"Can't parse date: {s}. Use e.g. 13/03 or 2026-03-13")


def parse_time(s):
    """'10:00' → time"""
    return datetime.strptime(s.strip().lower().replace('am', '').replace('pm', ''), '%H:%M').time()
