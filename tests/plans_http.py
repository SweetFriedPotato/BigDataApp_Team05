#!/usr/bin/env python3
from http_client import Client,DEFAULT
from pathlib import Path
import json,re
c=Client()
s,body,_=c.request('plan_form.php');assert s==200
token=c.token(body)
params={**DEFAULT,'action':'create','csrf_token':token,'plan_name':'HTTP <script>alert(1)</script>','memo':'<b>plain text</b>',
        'start_date':'2024-08-01','end_date':'2024-08-31','location_ids[]':[1,2]}
params.pop('apply_filters')
id=None
try:
    s,b,_=c.request('plan_actions.php',{**params,'csrf_token':'bad'},post=True);assert s==403
    s,b,_=c.request('plan_actions.php',{'action':'delete','plan_id':1});assert s==405
    s,b,_=c.request('plan_actions.php',{**params,'plan_name':'봄'*101},post=True);assert s==422 and 'Nothing was saved' in b
    s,b,_=c.request('plan_actions.php',{**params,'memo':'가'*2001},post=True);assert s==422
    s,b,_=c.request('plan_actions.php',params,post=True)
    assert s==200 and 'Plan saved with its selected locations.' in b and '&lt;script&gt;' in b and '<script>alert' not in b
    id=int(re.search(r'name="plan_id" value="(\d+)"',b).group(1))
    s,b,_=c.request('plans.php');assert s==200 and '&lt;script&gt;' in b
    updated={**params,'action':'update','plan_id':id,'plan_name':'Updated HTTP plan','location_ids[]':[3,5],'max_temp_threshold':'27.25'}
    s,b,_=c.request('plan_actions.php',updated,post=True);assert s==200 and 'Daegu, Jeju' in b and 'Updated HTTP plan' in b
    s,b,_=c.request('plan_actions.php',{'action':'apply','plan_id':id,'target':'window','csrf_token':token},post=True)
    assert s==200 and 'Saved comparison conditions applied' in b and 'value="27.25"' in b
    s,b,_=c.request('ranking.php');assert s==200 and 'value="27.25"' in b and 'value="3" checked' in b and 'value="1" checked' not in b
    s,b,_=c.request('plan_actions.php',{'action':'apply','plan_id':id,'target':'https://example.invalid','csrf_token':token},post=True);assert s==422
    s,b,_=c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token':token},post=True);assert s==200 and 'Plan and its selected locations deleted' in b
    s,b,_=c.request('plan_detail.php',{'id':id});assert s==404
    id=None
finally:
    if id is not None:c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token':token},post=True)
result={'result':'PASS','T21_T23':'Actual HTTP create/read/list/update/delete with PRG and persisted locations',
        'T26':'Apply restored common filters to window and reused them on ranking',
        'T27':'Escaped script/memo, CSRF403, GET405, overlength Unicode422, invalid redirect target422, deleted detail404',
        'test_records':'deleted in finally','client':'Python stdlib HTTP, Apache PHP 8.2'}
__import__('sys').path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from evidence_support import write_evidence
write_evidence('plans-http.json',result,['python3','tests/plans_http.py'],{'base_url':c.base,'client':'Python stdlib HTTP'},extra=['tests/plans_http.py','tests/http_client.py'])
print(json.dumps(result,indent=2))
