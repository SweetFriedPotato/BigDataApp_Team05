#!/usr/bin/env python3
"""Download each NASA point sequentially, preserving response bytes and provenance."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from data_common import ROOT, LOCATIONS, nasa_url, parse_nasa

manifest_path = ROOT / 'data/manifest.json'
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
manifest.update({'period': ['2023-01-01', '2025-12-31'], 'time_standard': 'LST',
                 'fields': {'tmean': 'T2M', 'tmax': 'T2M_MAX', 'tmin': 'T2M_MIN'},
                 'temperature_unit': 'C', 'coordinate_meaning': 'requested point, not grid center'})
manifest.setdefault('nasa', [])
for loc in LOCATIONS:
    path = ROOT / f'data/raw/nasa_{loc[1]}.csv'
    old = next((r for r in manifest['nasa'] if r['location_id'] == loc[0]), None)
    if path.exists() and old:
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != old['sha256']:
            raise ValueError('Existing raw hash changed; preserve and investigate')
        print(f'Reusing validated raw bytes: {path.name}', flush=True)
    else:
        url = nasa_url(loc)
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'SeasonalLivingGuide/1.0 academic data preparation'})
                with urllib.request.urlopen(request, timeout=55) as response:
                    if response.status != 200:
                        raise ValueError(f'HTTP {response.status}')
                    content = response.read()
                parse_nasa(content, loc[0])
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)
        path.write_bytes(content)
    _, validation = parse_nasa(content, loc[0])
    entry = {'location_id': loc[0], 'code': loc[1], 'requested_latitude': loc[4],
             'requested_longitude': loc[5], 'source_url': nasa_url(loc),
             'collected_at_utc': old['collected_at_utc'] if old else datetime.now(timezone.utc).isoformat(),
             'raw_file': str(path.relative_to(ROOT)), 'bytes': len(content),
             'sha256': hashlib.sha256(content).hexdigest(), 'validation': validation}
    manifest['nasa'] = sorted([r for r in manifest['nasa'] if r['location_id'] != loc[0]] + [entry], key=lambda r:r['location_id'])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(f'{loc[1]}: {validation}', flush=True)
