#!/usr/bin/env python3
"""Run real checks in the uniquely named committed-source evaluation server, never primary DB."""
import json,os,subprocess,sys
from pathlib import Path
from evidence_support import ROOT,evidence_dir,write_evidence
state=json.loads((ROOT/'.local/revision/evaluation.json').read_text(encoding='utf-8'))
assert state['prefix'].startswith('slg-review-')
def run(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(str(args)+p.stdout+p.stderr)
 return p.stdout
def php(file):return json.loads(run(['docker','exec',state['web'],'php','/workspace/tests/'+file+'.php']))
env={'base_url':state['url'],'source_commit':state['source_commit'],'app_sha256':state['app_sha256'],'container':state['web'],'document_root':'/var/www/html/team05','php':run(['docker','exec',state['web'],'php','-v']).splitlines()[0]}
baseline=php('fingerprint')
assert baseline==json.loads((ROOT/'docs/evidence/database-fingerprint.json').read_text(encoding='utf-8'))
for suite in ['schema','aggregate','olap','ranking','window','plans','seasonal','revision_plans','chart']:
 doc=php(suite);doc['result']='PASS' if all(t['status']=='PASS' for t in doc.get('tests',[])) else 'FAIL'
 name={'schema':'schema.json','revision_plans':'revision-plans.json'}.get(suite,suite+'-tests.json')
 write_evidence(name,doc,['docker','exec',state['web'],'php','/workspace/tests/'+suite+'.php'],env,extra=['tests/'+suite+'.php','tests/support.php','tools/run_checks.py'])
 assert doc['result']=='PASS',suite
 print(suite+': PASS',flush=True)
assert php('fingerprint')==baseline
os.environ['SLG_BASE_URL']=state['url']
for script in ['common_http','plans_http','adversarial_http','revision_http']:
 print(run([sys.executable,'tests/'+script+'.py']),flush=True)
assert php('fingerprint')==baseline,'HTTP test rows leaked'
a=json.loads((evidence_dir()/'revision-plans.json').read_text(encoding='utf-8'));b=json.loads((evidence_dir()/'revision-http.json').read_text(encoding='utf-8'))
write_evidence('revision-functional.json',{'result':'PASS','tests':a['tests']+b['tests'],'component_evidence':['revision-plans.json','revision-http.json'],'database_fingerprint_restored':True},['python3','tools/run_checks.py'],env,extra=['tools/run_checks.py','tests/revision_plans.php','tests/revision_http.py','tests/http_client.py'])
print('Disposable DB fingerprint unchanged: PASS')
