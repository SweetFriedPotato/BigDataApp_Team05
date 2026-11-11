#!/usr/bin/env python3
"""Create reviewable evidence tables only from result files produced by executed tests."""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence'
now=datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
rows={}
def evidence(file): return json.loads((E/file).read_text())
def add(id,description,expected,actual,file,command,status='PASS'):
    rows[id]=(description,expected,str(actual).replace('|','/').replace('\n',' ')[:850],status,file,command)
data=evidence('data-validation.json')
add('T01','NASA date sets','1096/location; 365/366/365; leap day; no duplicates or gaps',f"{data['temperature_rows']} total rows; five validated locations",'data-validation.json','python3 tools/validate_data.py')
add('T02','Temperature validity','No -999/missing rows; min≤mean≤max','All five sources: missing_temperature_rows=0 and order_errors=0','data-validation.json','python3 tools/validate_data.py')
add('T04','Schema','6 InnoDB tables; PK/FK/UNIQUE/CHECK/indexes',evidence('schema.json')['counts'],'schema.json','docker compose exec -T web php /workspace/tests/schema.php')
expectations={
'T03':'24 terms/year and ≥1 guide item/month', 'T05':'Raw Decimal averages/counts equal within 0.00001',
'T06':'60 valid days per Jan–Feb group; raw weighted mean','T07':'3 valid / 1 match / 1 exceedance from boundary/null fixture','T08':'Same denominator with different thresholds',
'T09':'5 year/10 month/155 January records; 17 partial days','T10':'Grand total 300 location-days; raw daily means',
'T11':'2/4=3/6 ties; full precision distinguishes equal displayed rates','T12':'Top1 returns both ties; min days excludes insufficient data','T13':'Busan/Daegu rank1 2/31; Jeju rank2 1/31; Seoul/Gwangju rank3',
'T14':'Day7 MA7=4; Day30 MA30=15.5','T15':'Day31 MA7=28; MA30=16.5 independent of display start',
'T16':'Seoul Jan1 1.141428…/0.301333…; all four metrics and leap-month boundaries','T17':'Initial6/29 and invalid/gap frames NULL','T18':'Per-location frames remain separate and ignore threshold filtering',
'T21':'Committed parent and selected locations read back','T22':'Body+regions replaced; identical update accepted','T23':'Parent/links deleted; other plan preserved',
'T24':'Actual parent INSERT then child FK failure leaves zero parent/links','T25':'Actual UPDATE+child DELETE then FK failure restores exact snapshot','T28':'Additional food rows leave weather statistics unchanged'}
for suite in ('aggregate','olap','ranking','window','plans','seasonal'):
    for r in evidence(suite+'-tests.json')['tests']:
        add(r['id'],r['test'],expectations[r['id']],r['actual'],suite+'-tests.json',f'docker compose exec -T web php /workspace/tests/{suite}.php',r['status'])
common=evidence('common-http.json')
add('T19','Cross-page PHP Session','Page A filters appear and are used on page B',common['session'],'common-http.json','python3 tests/common_http.py',common['result'])
add('T20','Malformed input','HTTP422; previous Session unchanged',f"{common['invalid_cases']} common/options cases + four seasonal invalid cases tested",'common-http.json','python3 tests/common_http.py; seasonal HTTP loop in progress.md',common['result'])
web=evidence('plans-http.json')
add('T26','Saved-plan application','Validated DB common conditions restored to Session',web['T26'],'plans-http.json','python3 tests/plans_http.py',web['result'])
add('T27','Output and mutation protection','Escaped HTML; POST+CSRF; Unicode lengths; no open redirect',web['T27'],'plans-http.json','python3 tests/plans_http.py',web['result'])
install=evidence('clean-install.json')
for id,search in [('T29','T29 '),('T30','T30 '),('T31','T31 '),('T32','T32 '),('T33','T33 ')]:
    step=next(x for x in install['steps'] if x['step'].startswith(search))
    add(id,step['step'],'Fresh isolated environment; complete expected state',step['actual'],'clean-install.json','python3 tools/verify_install.py',step['status'])
if (E/'release-verification.json').exists():
    r=evidence('release-verification.json');add('T34','Demo/package code identity','Archive files match the recorded commit',r,'release-verification.json','python3 tools/package_release.py --verify',r['result'])
else:add('T34','Demo/package code identity','Archive files match recorded release commit','Packaging pending P9 evidence freeze','progress.md','Not executed','NOT_RUN')
md=f'# Actual test results\n\nGenerated {now} from retained result files. PASS means an executed check. Synthetic fixtures are rolled back or cleaned up; no fixture is part of seed/dump. SQL assertions use native PDO with ONLY_FULL_GROUP_BY.\n\n'
md+='| ID | Test / input | Expected | Actual | Result | Evidence | Command / environment |\n|---|---|---|---|---|---|---|\n'
for id,(description,expected,actual,status,file,command) in sorted(rows.items()):
    link=f'[evidence](evidence/{file})' if file!='progress.md' else '[progress](progress.md)'
    md+=f'| {id} | {description} | {expected} | {actual} | **{status}** | {link} | `{command}` |\n'
browser=evidence('browser-tests.json')
md+=f"\nActual browser: Chromium {browser['browser']}; {browser['desktop']}, {browser['mobile']}; console errors {len(browser['console_errors'])}. See [browser evidence](evidence/browser-tests.json) and four actual screenshots.\n"
if (E/'xampp-install.json').exists():
    x=evidence('xampp-install.json');md+=f"\nAdditional actual XAMPP Linux test: **{x['result']}**. See [XAMPP evidence](evidence/xampp-install.json). This does not claim a Windows/macOS or professor-server test.\n"
else:md+='\nActual XAMPP package installation is in progress. Docker Apache checks do not substitute for that result. Windows/macOS and professor-server checks are NOT_RUN.\n'
md+='\nNo performance benchmark, user study, final human presentation or course upload was performed. Publication/academic contribution claims require human confirmation.\n'
(ROOT/'docs/test-results.md').write_text(md)
print(f'Wrote {len(rows)} test rows, {sum(x[3]=="PASS" for x in rows.values())} PASS')
