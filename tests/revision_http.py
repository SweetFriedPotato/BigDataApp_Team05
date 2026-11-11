#!/usr/bin/env python3
from http_client import Client,DEFAULT
from pathlib import Path
import html,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from evidence_support import write_evidence
cases=[]
def case(id,fn):
 try:cases.append({'id':id,'status':'PASS','actual':fn()})
 except Exception as e:cases.append({'id':id,'status':'FAIL','actual':str(e)})
def memo_cases():
 c=Client();actual=[]
 for memo in ['0','','한글 and English','<b>literal</b>']:
  id=None;s,b,_=c.request('plan_form.php');token=c.token(b)
  p={**DEFAULT,'action':'create','csrf_token':token,'plan_name':'T36 memo fixture','memo':memo};p.pop('apply_filters')
  try:
   s,b,_=c.request('plan_actions.php',p,post=True);assert s==200
   id=int(re.search(r'name="plan_id" value="(\d+)"',b).group(1))
   value=html.unescape(re.search(r'<p class="memo">(.*?)</p>',b,re.S).group(1))
   assert value==(memo if memo!='' else 'No memo.'),(memo,value)
   assert '<b>literal</b>' not in b
   actual.append({'input':memo,'display':value})
  finally:
   if id:c.request('plan_actions.php',{'action':'delete','plan_id':id,'csrf_token':token},post=True)
 return actual
def save_current():
 c=Client();p={**DEFAULT,'start_date':'2024-08-01','end_date':'2024-08-31'};assert c.request('aggregate.php',p)[0]==200
 current={**p,'start_date':'2024-01-01','end_date':'2024-01-03','location_ids[]':[2,3],'max_temp_threshold':'26.50','intent':'save','group_mode':'location_year'}
 s,b,_=c.request('aggregate.php',current);assert s==200 and '<h1>Create a Plan</h1>' in b,'Save conditions must forward current validated inputs to plan form'
 assert 'value="2024-01-01"' in b and 'value="26.50"' in b and 'value="2" checked' in b and 'value="1" checked' not in b
 assert c.request('plans.php')[1].count('T36 memo fixture')==0
 return {'dates':'2024-01-01..03','regions':[2,3],'threshold':'26.50','inserted_by_filter_save':False}
def invalid_save():
 c=Client();p={**DEFAULT,'max_temp_threshold':'27.50'};assert c.request('aggregate.php',p)[0]==200
 for change in [{'location_ids[]':[]},{'group_mode':'unknown'},{'intent':'https://example.invalid'}]:
  s,b,_=c.request('aggregate.php',{**p,'intent':'save',**change});assert s==422,(change,s)
  assert 'No analysis was run' in b
  s,b,_=c.request('ranking.php');assert s==200 and 'value="27.50"' in b
 return {'invalid_save_cases':3,'session':'previous conditions preserved','plan_insert':'not performed'}
case('T36',memo_cases);case('T37',save_current);case('T38',invalid_save)
write_evidence('revision-functional.json',{'result':'PASS' if all(c['status']=='PASS' for c in cases) else 'FAIL','tests':cases},['python3','tests/revision_http.py'],{'base_url':Client().base,'client':'Python stdlib HTTP'},extra=['tests/revision_http.py','tests/http_client.py'])
print(json.dumps(cases,ensure_ascii=False,indent=2));raise SystemExit(any(c['status']!='PASS' for c in cases))
