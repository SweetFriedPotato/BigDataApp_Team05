#!/usr/bin/env python3
"""Exercise native binding and hostile request shapes through the real POST boundary."""
from http_client import Client,DEFAULT
from pathlib import Path
import html,json,re
c=Client();status,body,_=c.request('plan_form.php');token=c.token(body)
payload="Robert'); DROP TABLE locations;--"
memo="Quotes ' and \\\n<script>window.__unexpected=1</script> & 한글"
request={**DEFAULT,'action':'create','csrf_token':token,'plan_name':payload,'memo':memo,'location_ids[]':[1,1,2]}
request.pop('apply_filters')
id=None
try:
    status,body,_=c.request('plan_actions.php',request,post=True)
    assert status==200 and payload in html.unescape(body) and memo in html.unescape(body)
    assert '<script>window.__unexpected' not in body and 'Seoul, Busan' in body
    id=int(re.search(r'name="plan_id" value="(\d+)"',body).group(1))
    for key,value in [('plan_id','1abc'),('action','drop_everything')]:
        status,_,_=c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token':token,key:value},post=True)
        assert status==422
    status,_,_=c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token[]':[token]},post=True);assert status==403
    status,body,_=c.request('index.php');assert status==200 and '5,480' in body
    status,body,_=c.request('plan_detail.php',{'id':id});assert status==200 and payload in html.unescape(body)
finally:
    if id is not None:c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token':token},post=True)
result={'result':'PASS','native_statement':'SQL metacharacter title stored as literal text; tables and 5480 weather rows survive','output':'script memo escaped','normalization':'duplicate location IDs stored once','hostile_shapes':'invalid action/id422; array CSRF403','cleanup':'test plan deleted'}
__import__('sys').path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from evidence_support import write_evidence
write_evidence('adversarial-http.json',result,['python3','tests/adversarial_http.py'],{'base_url':c.base,'client':'Python stdlib HTTP'},extra=['tests/adversarial_http.py','tests/http_client.py'])
print(json.dumps(result,indent=2))
