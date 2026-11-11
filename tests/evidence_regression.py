#!/usr/bin/env python3
"""Counterexamples for false PASSs. Fixtures never overwrite real execution evidence."""
import copy,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from evidence_support import metadata,write_evidence
from evidence_status import Store
from record_results import collect
from record_requirements import collect_requirements
checks=[]
def check(condition,message):
    if not condition:raise AssertionError(message)
    checks.append(message)
with tempfile.TemporaryDirectory(prefix='slg-status-fixtures-') as directory:
    base=Path(directory);normal=base/'normal';normal.mkdir()
    for source in (ROOT/'docs/evidence').glob('*.json'):shutil.copy2(source,normal/source.name)
    for path in normal.glob('*.json'):
        doc=json.loads(path.read_text(encoding='utf-8'));doc['_meta']=metadata(['fixture-only'],{'scope':'test fixture'},extra=['tools/record_results.py','tools/record_requirements.py','tools/evidence_status.py'])
        if path.name=='data-validation.json':
            doc['result']='PASS'
            for row in doc['nasa']:row['raw_sha256_match']=True
        path.write_text(json.dumps(doc),encoding='utf-8')
    rows=collect(Store(ROOT,normal))
    check(all(rows[id]['status']=='PASS' for id in ['T01','T02','T04']),'normal complete evidence produces PASS')
    failed=base/'failing';shutil.copytree(normal,failed)
    d=json.loads((failed/'data-validation.json').read_text(encoding='utf-8'));d['temperature_rows']=0
    for row in d['nasa']:row['missing_temperature_rows']=1
    (failed/'data-validation.json').write_text(json.dumps(d),encoding='utf-8')
    s=json.loads((failed/'schema.json').read_text(encoding='utf-8'));s['result']='FAIL';s['counts']['daily_temperatures']=0
    (failed/'schema.json').write_text(json.dumps(s),encoding='utf-8')
    rows=collect(Store(ROOT,failed));check(all(rows[id]['status']=='FAIL' for id in ['T01','T02','T04']),'audit counterexamples produce FAIL, including declared FAIL schema')
    check(rows['T02']['actual']['nasa'][0]['missing_temperature_rows']==1,'actual missing-row count is read from JSON')
    requirements=collect_requirements(Store(ROOT,failed));check(requirements['R02']['status']=='FAIL' and requirements['R03']['status']=='FAIL','failed data/schema propagate to mapped requirements')
    missing=base/'missing';missing.mkdir();rows=collect(Store(ROOT,missing))
    check(all(rows[id]['status']=='NOT_RUN' for id in ['T01','T02','T04']),'missing evidence is NOT_RUN')
    (normal/'data-validation.json').write_text(json.dumps({'result':'PASS','temperature_rows':5480,'_meta':metadata(['fixture'],{'fixture':True})}),encoding='utf-8')
    check(collect(Store(ROOT,normal))['T01']['status']=='PARTIAL','row count alone does not prove valid date sets')
    schema=json.loads((normal/'schema.json').read_text(encoding='utf-8'));schema.pop('_meta');(normal/'schema.json').write_text(json.dumps(schema),encoding='utf-8')
    check(collect(Store(ROOT,normal))['T04']['status']=='PARTIAL','missing execution provenance is not PASS')
    check(collect_requirements(Store(ROOT,missing))['R28']['status']!='PASS','report/diagram presence alone cannot satisfy R28')
    # CLI exit behavior is verified independently of imported functions.
    for fixture,expected in [(failed,1),(missing,1)]:
        p=subprocess.run([sys.executable,str(ROOT/'tools/record_results.py'),'--evidence-dir',str(fixture),'--output',str(base/'results.md'),'--ids','T01','T02','T04','--fail-on-error'],capture_output=True,text=True)
        check(p.returncode==expected,'strict mode rejects '+fixture.name)
        check('"PASS": 3' not in p.stdout,'no all-PASS summary for '+fixture.name)
    # Reproduce the historical bug in a disposable copy of the original generator.
    legacy=base/'legacy';(legacy/'tools').mkdir(parents=True);shutil.copytree(ROOT/'docs/evidence',legacy/'docs/evidence',ignore=shutil.ignore_patterns('revision-*','screenshots'))
    original=subprocess.check_output(['git','show','7c7c850:tools/record_results.py'],cwd=ROOT,text=True)
    (legacy/'tools/record_results.py').write_text(original,encoding='utf-8')
    for file in ('data-validation.json','schema.json'):shutil.copy2(failed/file,legacy/'docs/evidence'/file)
    p=subprocess.run([sys.executable,str(legacy/'tools/record_results.py')],text=True,capture_output=True)
    check(p.returncode==0 and '34 PASS' in p.stdout,'historical false-PASS behavior reproduced only in fixture')
write_evidence('evidence-regression.json',{'result':'PASS','fixture_classes':['normal','failing','missing'],'strict_exit_verified':True,'checks':checks,'historical_bug_reproduced':True},['python3','tests/evidence_regression.py'],extra=['tools/evidence_status.py','tools/evidence_support.py','tools/record_results.py','tools/record_requirements.py','tests/evidence_regression.py'])
print(json.dumps({'result':'PASS','checks':len(checks)},indent=2))
