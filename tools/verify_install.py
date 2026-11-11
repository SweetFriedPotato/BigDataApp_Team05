#!/usr/bin/env python3
"""Destructive checks are confined to new uniquely named containers/volume/network.
Never drops tables in the primary Compose DB. Requires existing local runtime images.
"""
import json
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prefix='slg-clean-'+uuid.uuid4().hex[:10]
network=prefix+'-net';volume=prefix+'-db';database=prefix+'-db';web=prefix+'-web'
results={'environment':'fresh MariaDB10.4 + PHP8.2/Apache containers; internal-only network','resource_prefix':prefix,'steps':[]}

def cmd(args,input=None,check=True):
    p=subprocess.run(args,input=input,text=True,capture_output=True,cwd=ROOT)
    if check and p.returncode:
        raise RuntimeError(f'{args[0:3]} exited {p.returncode}: {p.stderr[-3500:]} {p.stdout[-1500:]}')
    return p

def step(name,data):
    results['steps'].append({'step':name,'status':'PASS','actual':data});print(name+': PASS',flush=True)

def sql(text):
    return cmd(['docker','exec','-i','-e','MYSQL_PWD=team05',database,'mysql','-uteam05','--default-character-set=utf8mb4','team05'],text).stdout

def php(file):
    return json.loads(cmd(['docker','exec',web,'php','/workspace/tests/'+file]).stdout)

def wait_web():
    for _ in range(40):
        r=cmd(['docker','exec',web,'curl','-fsS','http://127.0.0.1/team05/'],check=False)
        if r.returncode==0:return
        time.sleep(1)
    raise RuntimeError('Fresh Apache did not become ready')

try:
    image=cmd(['docker','compose','images','-q','web']).stdout.strip()
    if not image:raise RuntimeError('Build the project runtime before running installation tests')
    with tempfile.TemporaryDirectory(prefix=prefix+'-') as tmp:
        snapshot=Path(tmp)
        for directory in ('team05','tests','docs/evidence'):
            shutil.copytree(ROOT/directory,snapshot/directory,ignore=shutil.ignore_patterns('config.local.php','__pycache__','screenshots'))
        cmd(['docker','network','create','--internal',network]);cmd(['docker','volume','create',volume])
        cmd(['docker','run','-d','--name',database,'--network',network,'--network-alias','db','--network-alias','database.local',
             '-e','MYSQL_ROOT_PASSWORD=isolated-test-only','-e','MYSQL_DATABASE=team05','-e','MYSQL_USER=team05','-e','MYSQL_PASSWORD=team05',
             '-v',volume+':/var/lib/mysql','mariadb:10.4'])
        for _ in range(60):
            ready=cmd(['docker','exec','-e','MYSQL_PWD=team05',database,'mysql','-uteam05','-e','SELECT 1','team05'],check=False)
            if ready.returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('Fresh database did not become ready')
        assert 'daily_temperatures' not in sql('SHOW TABLES;')
        sql((ROOT/'sql/dbcreate.sql').read_text()+(ROOT/'sql/dbinsert.sql').read_text())
        cmd(['docker','run','-d','--name',web,'--network',network,'-e','SLG_DB_HOST=db',
             '-v',str(snapshot/'team05')+':/var/www/html/team05:ro','-v',str(snapshot)+':/workspace:ro',image])
        wait_web()
        baseline=php('fingerprint.php')
        assert baseline==json.loads((ROOT/'docs/evidence/database-fingerprint.json').read_text()), 'Primary/fresh semantic fingerprints differ'
        schema=php('schema.php');assert schema['result']=='PASS'
        offline=php('offline_http.php');assert offline['result']=='PASS'
        step('T29 clean create→insert→all9screens',{'schema':schema['counts'],'identity':schema['identity'],'http':offline})
        suite={}
        for test in ('aggregate','olap','ranking','window','plans','seasonal'):
            report=php(test+'.php');assert all(r['status']=='PASS' for r in report['tests']),test
            suite[test]=[r['id'] for r in report['tests']]
        assert php('fingerprint.php')==baseline,'Synthetic test rows or plans leaked'
        step('fresh full calculation and transaction suite',suite)
        sql((ROOT/'sql/dbdrop.sql').read_text());assert sql('SHOW TABLES;').strip()==''
        sql((ROOT/'sql/dbcreate.sql').read_text()+(ROOT/'sql/dbinsert.sql').read_text());assert php('fingerprint.php')==baseline
        step('T30 drop→create→insert',{'fingerprint':'identical rows, data hashes, columns, constraints and indexes'})
        sql((ROOT/'sql/dbdrop.sql').read_text());assert sql('SHOW TABLES;').strip()==''
        sql((ROOT/'sql/dbdump.sql').read_text());assert php('fingerprint.php')==baseline
        restored=php('offline_http.php');assert restored['result']=='PASS'
        step('T31 dump-only restore into zero tables',{'fingerprint':'identical to seeded baseline','http':restored,'client':'mysql bundled with MariaDB10.4.34'})
        internal=json.loads(cmd(['docker','network','inspect',network]).stdout)[0]['Internal'];assert internal
        only_networks=json.loads(cmd(['docker','inspect',web]).stdout)[0]['NetworkSettings']['Networks'];assert list(only_networks)==[network]
        egress=cmd(['docker','exec',web,'curl','-fsS','--connect-timeout','2','--max-time','3','https://example.com'],check=False)
        assert egress.returncode!=0,'Unexpected public network access'
        step('T32 offline runtime',{'internal_network':True,'attached_networks':list(only_networks),'public_request_exit':egress.returncode,'all9screens_and_crud':'passed before and after dump restore'})
        (snapshot/'team05/config.local.php').write_text("<?php return ['host'=>'database.local','port'=>3306];\n")
        effective=cmd(['docker','exec',web,'php','-r',"$c=require '/var/www/html/team05/config.php';echo $c['host'];"]).stdout
        assert effective=='database.local'
        assert php('offline_http.php')['result']=='PASS'
        assert php('fingerprint.php')==baseline
        step('T33 changed copied path and local config override',{'copied_path':str(snapshot/'team05'),'web_path':'/var/www/html/team05','url':'http://127.0.0.1/team05/','override_host':effective,'account':'team05@%','default_user_database_password':'team05; root not used by application'})
        results['result']='PASS'
except Exception as e:
    results['result']='FAIL';results['error']=str(e)
    raise
finally:
    for name in (web,database):cmd(['docker','rm','-f',name],check=False)
    cmd(['docker','volume','rm',volume],check=False);cmd(['docker','network','rm',network],check=False)
    results['cleanup']='only this run’s unique resources removed; primary runtime preserved'
    (ROOT/'docs/evidence/clean-install.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
