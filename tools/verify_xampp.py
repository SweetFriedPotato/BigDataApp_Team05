#!/usr/bin/env python3
"""Run official XAMPP in a fresh no-network container at its actual htdocs/team05 path."""
import hashlib,json,shutil,subprocess,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from evidence_support import write_evidence
name='slg-xampp-'+uuid.uuid4().hex[:10]
report={'environment':'official XAMPP Linux8.2.12 in fresh Ubuntu22.04 container; network=none','steps':[]}
def call(args,input=None,check=True):
    p=subprocess.run(args,input=input,text=True,capture_output=True,cwd=ROOT)
    if check and p.returncode:raise RuntimeError(f'{args[:4]} exit {p.returncode}: {p.stderr[-2500:]} {p.stdout[-2500:]}')
    return p

def execute(args,input=None,check=True):return call(['docker','exec','-i',name,*args],input,check)
def sql(text,root=False):
    args=['/opt/lampp/bin/mysql','--default-character-set=utf8mb4']
    args+=['-uroot'] if root else ['-uteam05','-pteam05','team05']
    return execute(args,text).stdout

def php(script):return json.loads(execute(['/opt/lampp/bin/php','/workspace/tests/'+script]).stdout)
def step(label,actual):report['steps'].append({'step':label,'status':'PASS','actual':actual});print(label+': PASS',flush=True)
try:
    with tempfile.TemporaryDirectory(prefix=name+'-') as tmp:
        snapshot=Path(tmp)
        for folder in ('team05','tests','docs/evidence'):
            shutil.copytree(ROOT/folder,snapshot/folder,ignore=shutil.ignore_patterns('config.local.php','__pycache__','screenshots'))
        call(['docker','run','-d','--name',name,'--network','none',
              '-v',str(snapshot/'team05')+':/opt/lampp/htdocs/team05:ro','-v',str(snapshot)+':/workspace:ro','seasonal-team05-xampp:8.2.12'])
        apache=execute(['/opt/lampp/lampp','startapache']).stdout
        mysql=execute(['/opt/lampp/lampp','startmysql']).stdout
        for _ in range(40):
            ping=execute(['/opt/lampp/bin/mysqladmin','-uroot','ping'],check=False)
            if ping.returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('XAMPP MariaDB did not start')
        sql("CREATE DATABASE team05 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER 'team05'@'localhost' IDENTIFIED BY 'team05'; GRANT ALL PRIVILEGES ON team05.* TO 'team05'@'localhost';",root=True)
        versions={'php':execute(['/opt/lampp/bin/php','-v']).stdout,'apache':execute(['/opt/lampp/bin/httpd','-v']).stdout,'mysql_client':execute(['/opt/lampp/bin/mysql','--version']).stdout,'mysqldump':execute(['/opt/lampp/bin/mysqldump','--version']).stdout}
        report['versions']=versions
        probe=snapshot/'team05/_xampp_probe.php'
        probe.write_text("<?php header('Content-Type: application/json'); echo json_encode(['sapi'=>PHP_SAPI,'version'=>PHP_VERSION,'pdo_mysql'=>extension_loaded('pdo_mysql'),'ini'=>php_ini_loaded_file()]);", encoding='utf-8')
        try:
            apache_php=json.loads(execute(['curl','-fsS','http://127.0.0.1/team05/_xampp_probe.php']).stdout)
            assert apache_php['sapi']=='apache2handler' and apache_php['pdo_mysql']
            report['apache_php']=apache_php
        finally: probe.unlink()
        step('new official XAMPP started',{'apache':apache,'mysql':mysql,'htdocs':'/opt/lampp/htdocs/team05','config':'unmodified public defaults; no environment override','network':'none'})
        sql((ROOT/'sql/dbcreate.sql').read_text(encoding='utf-8')+(ROOT/'sql/dbinsert.sql').read_text(encoding='utf-8'))
        baseline=php('fingerprint.php')
        assert baseline==json.loads((ROOT/'docs/evidence/database-fingerprint.json').read_text(encoding='utf-8')),'XAMPP seeded fingerprint differs'
        schema=php('schema.php');assert schema['result']=='PASS'
        http=php('offline_http.php');assert http['result']=='PASS'
        step('create→insert→all9screens and web CRUD',{'schema_counts':schema['counts'],'identity':schema['identity'],'http':http})
        suites={}
        for test in ('aggregate','olap','ranking','window','plans','seasonal','revision_plans','chart'):
            r=php(test+'.php');assert all(t['status']=='PASS' for t in r['tests']),test;suites[test]=[t['id'] for t in r['tests']]
        assert php('fingerprint.php')==baseline
        step('all calculations and real rollback tests',suites)
        sql((ROOT/'sql/dbdrop.sql').read_text(encoding='utf-8'));assert sql('SHOW TABLES;').strip()==''
        sql((ROOT/'sql/dbcreate.sql').read_text(encoding='utf-8')+(ROOT/'sql/dbinsert.sql').read_text(encoding='utf-8'));assert php('fingerprint.php')==baseline
        step('drop→create→insert',{'fingerprint':'identical'})
        sql((ROOT/'sql/dbdrop.sql').read_text(encoding='utf-8'));assert sql('SHOW TABLES;').strip()==''
        sql((ROOT/'sql/dbdump.sql').read_text(encoding='utf-8'));assert php('fingerprint.php')==baseline
        assert php('offline_http.php')['result']=='PASS'
        step('project dump restored by actual XAMPP mysql client',{'fingerprint':'all rows, columns, PK/FK/CHECK/indexes identical','http':'all screens and CRUD passed'})
        local=snapshot/'team05/config.local.php';local.write_text("<?php return ['host'=>'localhost','port'=>3306];\n", encoding='utf-8')
        # localhost uses XAMPP's configured local socket; confirms a real local-override path.
        assert php('offline_http.php')['result']=='PASS';local.unlink()
        step('local configuration override',{'host':'localhost','port':3306,'result':'all screens and CRUD passed'})
        settings=execute(['/opt/lampp/bin/php','-r',"echo json_encode(['sapi'=>PHP_SAPI,'pdo_mysql'=>extension_loaded('pdo_mysql'),'ini'=>php_ini_loaded_file()]);"]).stdout
        report['cli_settings']=json.loads(settings)
        mode=json.loads(call(['docker','inspect',name]).stdout)[0]['HostConfig']['NetworkMode'];assert mode=='none'
        step('offline runtime',{'docker_network_mode':mode,'web_needs':'PHP + MariaDB only; no API/CDN/Node/Python'})
        report['result']='PASS'
except Exception as e:
    report['result']='FAIL';report['error']=str(e);raise
finally:
    call(['docker','rm','-f',name],check=False)
    report['cleanup']='fresh XAMPP container and temporary copied source removed; primary runtime untouched'
    report['installer']={'url':'https://downloads.sourceforge.net/project/xampp/XAMPP%20Linux/8.2.12/xampp-linux-x64-8.2.12-0-installer.run','sha256':'df0774e7a6d0d0754a5f0132015411234b5f953df2365b693d3758fc35a30374','note':'hash of downloaded bytes; not claimed as independently signed vendor checksum'}
    write_evidence('xampp-install.json',report,['python3','tools/verify_xampp.py'],report.get('versions',{'environment':report['environment']}),extra=['tools/verify_xampp.py','tests/offline_http.php','tests/fingerprint.php','tests/revision_plans.php','tests/chart.php'])
