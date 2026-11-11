#!/usr/bin/env python3
"""Independent Decimal reference calculation directly from original NASA CSV bytes."""
import csv
import io
import json
import hashlib
from pathlib import Path
from datetime import date,timedelta
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
raw={}
hashes={}
for i,code in enumerate(('seoul','busan','daegu','gwangju','jeju'),1):
    content=(ROOT/f'data/raw/nasa_{code}.csv').read_bytes()
    hashes[code]=hashlib.sha256(content).hexdigest()
    body=content.decode().split('-END HEADER-')[1].strip()
    raw[i]={date(int(r['YEAR']),int(r['MO']),int(r['DY'])):
        tuple(Decimal(r[k]) for k in ('T2M','T2M_MAX','T2M_MIN')) for r in csv.DictReader(io.StringIO(body))}
aug=[]
for i,series in raw.items():
    vals=[v for day,v in series.items() if day.year==2024 and day.month==8]
    count=sum(high<=28 and high-low<=10 for mean,high,low in vals)
    aug.append({'location_id':i,'valid_days':len(vals),'matching_days':count,'matching_rate':str(Decimal(count)*100/len(vals))})
ranked_rates=sorted({Decimal(r['matching_rate']) for r in aug},reverse=True)
for r in aug:r['rank_no']=ranked_rates.index(Decimal(r['matching_rate']))+1
aug.sort(key=lambda r:(r['rank_no'],r['location_id']))
groups=[]
for i,series in raw.items():
    for month in (None,1,2):
        vals=[v for day,v in series.items() if day.year==2024 and day.month in (1,2) and (month is None or day.month==month)]
        means,highs,lows=zip(*vals)
        avg=lambda vs:str(sum(vs)/len(vs))
        groups.append({'location_id':i,'month_no':month,'valid_days':len(vals),
            'mean_temperature':avg(means),'mean_daily_max':avg(highs),'mean_daily_min':avg(lows),
            'mean_daily_range':avg([h-l for _,h,l in vals]),'period_high':str(max(highs)),'period_low':str(min(lows)),
            'matching_days':sum(h<=28 and h-l<=10 for _,h,l in vals), 'exceedance_days':sum(h>28 for _,h,l in vals)})
windows=[]
for i in raw:
    for day in (date(2024,1,1),date(2024,3,1)):
        for metric,fn in [('mean',lambda v:v[0]),('max',lambda v:v[1]),('min',lambda v:v[2]),('range',lambda v:v[1]-v[2])]:
            windows.append({'location_id':i,'weather_date':day.isoformat(),'metric':metric,
                **{f'ma{n}':str(sum(fn(raw[i][day-timedelta(days=k)]) for k in range(n))/n) for n in (7,30)}})
expected={'raw_sha256':hashes,'ranking_august_2024':aug,'aggregate_jan_feb_2024':groups,'windows':windows}
__import__('sys').path.insert(0,str(ROOT/'tools'))
from evidence_support import write_evidence
write_evidence('oracle.json',expected,['python3','tests/oracle.py'],group='data',extra=['tests/oracle.py'])
print(json.dumps({'ranking_august_2024':aug,'seoul_january_1':windows[0]},indent=2))
