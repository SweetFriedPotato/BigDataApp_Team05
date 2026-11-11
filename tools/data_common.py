"""Developer-only data preparation. Runtime uses the committed SQL, never this API."""
import csv
import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCATIONS = [
    (1, 'seoul', 'Seoul', '서울', '37.5665', '126.9780'),
    (2, 'busan', 'Busan', '부산', '35.1796', '129.0756'),
    (3, 'daegu', 'Daegu', '대구', '35.8714', '128.6014'),
    (4, 'gwangju', 'Gwangju', '광주', '35.1595', '126.8526'),
    (5, 'jeju', 'Jeju', '제주', '33.4996', '126.5312'),
]
START, END = date(2023, 1, 1), date(2025, 12, 31)
EXPECTED = {START + timedelta(days=i) for i in range((END-START).days+1)}

def nasa_url(location):
    return ('https://power.larc.nasa.gov/api/temporal/daily/point?'
            'parameters=T2M,T2M_MAX,T2M_MIN&community=RE&'
            f'longitude={location[5]}&latitude={location[4]}&'
            'start=20230101&end=20251231&format=CSV&time-standard=LST')

def parse_nasa(content, location_id):
    lines = content.decode('utf-8-sig').splitlines()
    marker = next((i for i, line in enumerate(lines) if line.strip() == '-END HEADER-'), None)
    if marker is None:
        raise ValueError('NASA header terminator missing; refusing non-CSV response')
    reader = csv.DictReader(io.StringIO('\n'.join(lines[marker+1:])), skipinitialspace=True)
    required = {'YEAR', 'MO', 'DY', 'T2M', 'T2M_MAX', 'T2M_MIN'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError(f'Unexpected CSV columns: {reader.fieldnames}')
    rows, seen, missing, order_errors = [], set(), 0, 0
    for record in reader:
        day = date(int(record['YEAR']), int(record['MO']), int(record['DY']))
        if day in seen:
            raise ValueError(f'Duplicate date {day}')
        seen.add(day)
        vals = []
        for key in ('T2M', 'T2M_MAX', 'T2M_MIN'):
            value = record[key].strip()
            try:
                num = Decimal(value) if value else None
            except InvalidOperation as exc:
                raise ValueError(f'Invalid number {value}') from exc
            if num is not None and (not num.is_finite() or num < -999):
                raise ValueError('Non-finite/out-of-range temperature')
            vals.append(None if num == Decimal('-999') else num)
        mean, high, low = vals
        missing += any(v is None for v in vals)
        order_errors += any(a is not None and b is not None and a > b
                            for a, b in ((low, mean), (mean, high), (low, high)))
        rows.append([location_id, day.isoformat(), *[str(v) if v is not None else None for v in vals]])
    report = {'rows': len(rows), 'missing_dates': len(EXPECTED-seen),
              'outside_dates': len(seen-EXPECTED), 'duplicates': 0,
              'missing_temperature_rows': missing, 'order_errors': order_errors,
              'year_counts': {str(y): sum(d.year == y for d in seen) for y in (2023, 2024, 2025)},
              'leap_day': date(2024, 2, 29) in seen}
    if seen != EXPECTED or len(rows) != 1096 or missing or order_errors:
        raise ValueError(f'Data validation failed: {report}')
    return sorted(rows, key=lambda r: r[1]), report
