#!/usr/bin/env python3
"""Validate raw inputs before writing deterministic normalized CSVs."""
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from data_common import ROOT, LOCATIONS, parse_nasa

def validate():
    manifest = json.loads((ROOT/'data/manifest.json').read_text())
    all_rows, reports = [], []
    for loc in LOCATIONS:
        content = (ROOT/f'data/raw/nasa_{loc[1]}.csv').read_bytes()
        entry = next(r for r in manifest['nasa'] if r['location_id'] == loc[0])
        assert hashlib.sha256(content).hexdigest() == entry['sha256'], 'Raw hash mismatch'
        rows, report = parse_nasa(content, loc[0])
        all_rows.extend(rows)
        reports.append({'location': loc[1], **report})
    with (ROOT/'data/raw/kasi_reference.csv').open() as f:
        terms = list(csv.DictReader(f))
    assert len(terms) == 72 and len({r['term_date'] for r in terms}) == 72
    assert Counter(date.fromisoformat(r['term_date']).year for r in terms) == {2023:24, 2024:24, 2025:24}
    with (ROOT/'data/raw/rda_curated.csv').open() as f:
        foods = list(csv.DictReader(f))
    assert len(foods) == 12 and {int(r['month_no']) for r in foods} == set(range(1,13))
    assert len({(r['month_no'], r['food_name']) for r in foods}) == 12
    for name, header, rows in [
        ('temperatures', ['location_id','weather_date','tmean','tmax','tmin'], all_rows),
        ('solar_terms', ['term_date','term_name','source_url'], [[r[k] for k in ('term_date','term_name','source_url')] for r in sorted(terms,key=lambda r:r['term_date'])]),
        ('monthly_food_guides', ['month_no','food_name','source_url'], [[r[k] for k in ('month_no','food_name','source_url')] for r in foods])]:
        with (ROOT/f'data/processed/{name}.csv').open('w', newline='') as f:
            writer = csv.writer(f, lineterminator='\n'); writer.writerow(header); writer.writerows(rows)
    result = {'nasa': reports, 'temperature_rows': len(all_rows), 'solar_terms':len(terms), 'food_guides':len(foods)}
    (ROOT/'docs/evidence/data-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return all_rows, terms, foods

if __name__ == '__main__':
    validate()
