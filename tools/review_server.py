#!/usr/bin/env python3
"""Deploy a committed ZIP to an isolated real Apache document root and inspect its bytes."""
import argparse,hashlib,json,shutil,subprocess,time,uuid,zipfile
from pathlib import Path
from evidence_support import ROOT,evidence_dir,write_evidence
from app_identity import committed_identity,canonical_hash

def call(args,data=None,check=True):
    p=subprocess.run(args,input=data,text=True,capture_output=True,encoding='utf-8')
    if check and p.returncode:raise RuntimeError(str(args[:3])+': '+p.stderr+p.stdout[-1800:])
    return p

def inspect(state,identity):
    code='''$root='/var/www/html/team05/';$a=[];$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));foreach($it as $f)if($f->isFile()){$a[substr($f->getPathname(),strlen($root))]=hash_file('sha256',$f->getPathname());}ksort($a);echo json_encode($a);'''
    actual=json.loads(call(['docker','exec',state['web'],'php','-r',code]).stdout)
    assert actual==identity['app_files'],'Actual serving document root differs from committed app manifest'
    for relative in actual:
        if relative.startswith('assets/'):
            response=subprocess.run(['curl','-fsS',state['url']+relative],capture_output=True)
            assert response.returncode==0 and hashlib.sha256(response.stdout).hexdigest()==actual[relative],'HTTP asset mismatch: '+relative
    return {'result':'PASS','source_commit':identity['source_commit'],'app_sha256':canonical_hash(actual),'served_files':actual,'document_root':'/var/www/html/team05','url':state['url'],'container':state['web'],'server_config':call(['docker','exec',state['web'],'apache2ctl','-S']).stdout.strip(),'scope':'Actual container PHP/CSS/JS/SVG/font/other bytes and HTTP-served static assets checked'}

def stop(state):
    assert state['prefix'].startswith('slg-review-')
    for name in ('web','db'):call(['docker','rm','-f',state[name]],check=False)
    call(['docker','volume','rm',state['volume']],check=False)
    for name in ('internal','access'):call(['docker','network','rm',state[name]],check=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','verify','stop']);p.add_argument('--commit',default='HEAD');p.add_argument('--archive',type=Path);p.add_argument('--port',type=int,default=8057);p.add_argument('--state',type=Path,default=ROOT/'.local/revision/evaluation.json');a=p.parse_args()
    if a.action!='start':
        state=json.loads(a.state.read_text(encoding='utf-8'))
        if a.action=='stop':stop(state);return
        identity=json.loads((evidence_dir()/'app-source.json').read_text(encoding='utf-8'));proof=inspect(state,identity);write_evidence('served-app.json',proof,['python3','tools/review_server.py','verify'],{'url':state['url'],'document_root':proof['document_root']},extra=['tools/review_server.py','tools/app_identity.py']);print(json.dumps(proof,indent=2));return
    if a.state.exists():raise RuntimeError('Evaluation state already exists; verify or stop explicitly rather than resetting its DB')
    identity=committed_identity(a.commit);prefix='slg-review-'+uuid.uuid4().hex[:9];directory=ROOT/'.local/revision'/prefix;source=directory/'source';source.mkdir(parents=True)
    archive=a.archive or directory/'committed-source.zip'
    if not a.archive:
        data=subprocess.check_output(['git','archive','--format=zip',identity['source_commit']],cwd=ROOT);archive.write_bytes(data)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():assert (source/name).resolve().is_relative_to(source.resolve())
        z.extractall(source)
    for name,digest in identity['app_files'].items():assert hashlib.sha256((source/'team05'/name).read_bytes()).hexdigest()==digest
    state={'prefix':prefix,'web':prefix+'-web','db':prefix+'-db','internal':prefix+'-dbnet','access':prefix+'-access','volume':prefix+'-volume','url':f'http://127.0.0.1:{a.port}/team05/','source':str(source),'archive':str(archive),'source_commit':identity['source_commit'],'app_sha256':identity['app_sha256']}
    try:
        call(['docker','network','create','--internal',state['internal']]);call(['docker','network','create',state['access']]);call(['docker','volume','create',state['volume']])
        call(['docker','run','-d','--name',state['db'],'--network',state['internal'],'--network-alias','db','-e','MYSQL_ROOT_PASSWORD=review-disposable-only','-e','MYSQL_DATABASE=team05','-e','MYSQL_USER=team05','-e','MYSQL_PASSWORD=team05','-v',state['volume']+':/var/lib/mysql','mariadb:10.4'])
        for _ in range(50):
            if call(['docker','exec','-e','MYSQL_PWD=team05',state['db'],'mysql','-uteam05','-e','SELECT 1','team05'],check=False).returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('Evaluation DB did not start')
        sql=(source/'sql/dbcreate.sql').read_text(encoding='utf-8')+(source/'sql/dbinsert.sql').read_text(encoding='utf-8');call(['docker','exec','-i','-e','MYSQL_PWD=team05',state['db'],'mysql','-uteam05','--default-character-set=utf8mb4','team05'],sql)
        call(['docker','run','-d','--name',state['web'],'--network',state['access'],'-p',f'127.0.0.1:{a.port}:80','-e','SLG_DB_HOST=db','-v',str(source/'team05')+':/var/www/html/team05:ro','-v',str(source)+':/workspace:ro','-v',str(ROOT/'tests')+':/workspace/tests:ro','seasonal-team05-web:latest'])
        call(['docker','network','connect',state['internal'],state['web']])
        for _ in range(30):
            if call(['curl','-fsS',state['url']],check=False).returncode==0:break
            time.sleep(1)
        else:raise RuntimeError('Evaluation HTTP did not start')
        a.state.parent.mkdir(parents=True,exist_ok=True);a.state.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
        proof=inspect(state,identity);write_evidence('served-app.json',proof,['python3','tools/review_server.py','start','--commit',identity['source_commit']],{'url':state['url'],'document_root':proof['document_root']},extra=['tools/review_server.py','tools/app_identity.py']);print(json.dumps(state,indent=2))
    except Exception:stop(state);raise
if __name__=='__main__':main()
