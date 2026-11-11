"""Fail-closed interpretation of executed evidence; no default PASSs."""
import hashlib,json
from datetime import datetime
from pathlib import Path
STATES={'PASS','FAIL','NOT_RUN','PARTIAL','BLOCKED'}
EXPECTED_COUNTS={'daily_temperatures':5480,'locations':5,'monthly_food_guides':12,'plan_locations':0,'saved_plans':0,'solar_terms':72}
def combine(states):
    states=list(states)
    if not states or all(s=='NOT_RUN' for s in states):return 'NOT_RUN'
    if 'FAIL' in states:return 'FAIL'
    if 'BLOCKED' in states:return 'BLOCKED'
    return 'PASS' if all(s=='PASS' for s in states) else 'PARTIAL'
class Store:
    def __init__(self,root,directory):self.root=Path(root);self.directory=Path(directory)
    def read(self,name):
        path=self.directory/name
        if not path.exists():return None,'NOT_RUN','Evidence file not present'
        try:return json.loads(path.read_text(encoding='utf-8')),None,None
        except (ValueError,OSError) as e:return None,'FAIL','Unreadable evidence: '+str(e)
    def provenance(self,doc):
        meta=doc.get('_meta',{})
        if not all(meta.get(k) for k in ('executed_at','command','environment','source_files')):return 'PARTIAL','Missing execution time/command/environment/input hashes; not a current verified run'
        try:
            stamp=datetime.fromisoformat(meta['executed_at'])
            if stamp.tzinfo is None:raise ValueError('No timezone')
        except (ValueError,TypeError):return 'PARTIAL','Invalid execution timestamp'
        if not isinstance(meta['source_files'],dict):return 'PARTIAL','Input manifest absent'
        changed=[]
        for name,expected in meta['source_files'].items():
            path=(self.root/name).resolve()
            if not path.is_relative_to(self.root.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:changed.append(name)
        return ('PARTIAL','Executed input files changed: '+', '.join(changed[:5])) if changed else ('PASS','Execution metadata and tested file hashes verified')
    def result(self,name,validator=None,test_id=None,step=None):
        doc,status,reason=self.read(name)
        if status:return {'status':status,'actual':reason,'evidence':name,'execution':None}
        actual=doc;declared=doc.get('result')
        if test_id:
            matches=[r for r in doc.get('tests',[]) if r.get('id')==test_id]
            if len(matches)!=1:return {'status':(doc.get('result') if doc.get('result') in ('FAIL','BLOCKED') else 'NOT_RUN') if not matches else 'FAIL','actual':doc.get('error','Test row missing or duplicated'),'evidence':name,'execution':doc.get('_meta')}
            actual=matches[0];declared=actual.get('status')
        if step:
            matches=[r for r in doc.get('steps',[]) if r.get('step','').startswith(step)]
            if len(matches)!=1:return {'status':'NOT_RUN','actual':'Required installation step not present','evidence':name,'execution':doc.get('_meta')}
            actual=matches[0];declared=actual.get('status')
        status=declared if declared in STATES else 'PARTIAL'
        reasons=[]
        if validator:
            checks=validator(actual if (test_id or step) else doc)
            if any(v is False for _,v in checks):status='FAIL'
            elif status not in ('FAIL','BLOCKED','NOT_RUN') and any(v is None for _,v in checks):status='PARTIAL'
            reasons=[key+(': missing' if value is None else ': mismatch') for key,value in checks if value is not True]
        if test_id and 'actual' not in actual and status=='PASS':status='PARTIAL';reasons.append('actual test result missing')
        if status=='PASS':
            provenance,reason=self.provenance(doc)
            status=provenance
            if provenance!='PASS':reasons.append(reason)
        return {'status':status,'actual':actual,'evidence':name,'notes':reasons,'execution':doc.get('_meta')}
def field(doc,key,expected):return None if key not in doc else doc[key]==expected
def data_checks(doc,temperatures=False):
    nasa=doc.get('nasa');checks=[('temperature_rows',field(doc,'temperature_rows',5480)),('five NASA locations',None if nasa is None else isinstance(nasa,list) and len(nasa)==5)]
    if not isinstance(nasa,list):return checks
    for i,row in enumerate(nasa):
        if temperatures:
            keys={'missing_temperature_rows':0,'order_errors':0,'raw_sha256_match':True}
        else:keys={'rows':1096,'missing_dates':0,'outside_dates':0,'duplicates':0,'year_counts':{'2023':365,'2024':366,'2025':365},'leap_day':True}
        checks += [(f'location {i+1} {key}',field(row,key,value)) for key,value in keys.items()]
    return checks
def schema_checks(doc):
    checks=[('initial row counts',field(doc,'counts',EXPECTED_COUNTS))]
    tables=doc.get('tables');checks.append(('six tables',None if tables is None else len(tables)==6))
    if isinstance(tables,list):checks += [(t.get('TABLE_NAME','table')+' engine/collation',t.get('ENGINE')=='InnoDB' and t.get('TABLE_COLLATION')=='utf8mb4_unicode_ci') for t in tables]
    constraints=doc.get('constraints');indexes=doc.get('indexes')
    checks += [('six primary keys',None if constraints is None else sum(x.get('CONSTRAINT_TYPE')=='PRIMARY KEY' for x in constraints)==6),('three FKs',None if constraints is None else sum(x.get('CONSTRAINT_TYPE')=='FOREIGN KEY' for x in constraints)==3),('date/location index',None if indexes is None else any(x.get('INDEX_NAME')=='idx_weather_date_location' for x in indexes))]
    return checks
