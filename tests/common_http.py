#!/usr/bin/env python3
from http_client import Client,DEFAULT
from pathlib import Path
import json
c=Client()
f={**DEFAULT,'start_date':'2024-08-01','end_date':'2024-08-31','location_ids[]':[2,3],'max_temp_threshold':'27.50'}
status,body,headers=c.request('aggregate.php',f)
assert status==200
status,body,_=c.request('ranking.php')
assert status==200 and 'value="2024-08-01"' in body and 'value="27.50"' in body
assert 'value="2" checked' in body and 'value="3" checked' in body and 'value="1" checked' not in body
bad=[{'location_ids[]':[]},{'location_ids[]':['1abc']},{'location_ids[]':[99]},
     {'start_date':'2024-02-30'},{'start_date':'2025-01-01','end_date':'2024-01-01'},
     {'max_temp_threshold':'NaN'},{'max_temp_threshold':'INF'},{'max_temp_threshold':'28.001'},
     {'max_temp_range':'-1'},{'max_temp_range':'0 OR 1=1'}, {'start_date[]':['2024-01-01']},
     {'group_mode':'location_year; DROP TABLE locations'}]
for change in bad:
    status,body,_=c.request('aggregate.php',{**f,**change})
    assert status==422 and 'No analysis was run' in body,(change,status)
    status,after,_=c.request('ranking.php')
    assert status==200 and 'value="27.50"' in after and 'value="2024-08-01"' in after
status,body,_=c.request('window.php',{'window_days':8})
assert status==422
status,body,_=c.request('aggregate.php')
token=c.token(body)
assert 'HttpOnly' in str(headers) and 'SameSite=Lax' in str(headers)
status,body,_=c.request('aggregate.php',{'reset_filters':1,'csrf_token':'bad'},post=True)
assert status==422
status,body,_=c.request('aggregate.php',{'reset_filters':1,'csrf_token':token},post=True)
assert status==200 and 'value="2025-01-01"' in body and c.token(body)==token
for page in ('config.php','config.local.example.php','includes/db.php'):
    status,body,_=c.request(page)
    assert status==403,(page,status)
assert "default-src 'self'" in headers['Content-Security-Policy']
result={'result':'PASS','session':'A aggregate filters reused by B ranking; invalid common/option submissions preserve prior state; reset preserves CSRF',
    'invalid_cases':len(bad)+1,'protected_files':'config and includes return HTTP 403','cookies':'HttpOnly, SameSite=Lax','environment':{'base_url':c.base,'http_server':headers.get('Server','not exposed'),'network_isolation':'not inspected by HTTP helper'}}
__import__('sys').path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from evidence_support import write_evidence
write_evidence('common-http.json',result,['python3','tests/common_http.py'],result['environment'],extra=['tests/common_http.py','tests/http_client.py'])
print(json.dumps(result,indent=2))
