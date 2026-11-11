#!/usr/bin/env python3
"""Verify a committed payload, actual serving root and captured app as distinct scopes."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from evidence_support import ROOT,evidence_dir,write_evidence
from app_identity import committed_identity
from review_server import inspect
DIST=ROOT/'dist'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--record-evidence',action='store_true',help='Record this concrete snapshot once, then commit docs; final packaging need not rewrite tracked evidence');a=parser.parse_args()
 dirty=git('status','--porcelain','--untracked-files=normal').decode().strip()
 if dirty:raise RuntimeError('Review and commit all changes before packaging: '+dirty[:1800])
 commit=git('rev-parse','HEAD').decode().strip();identity=json.loads((evidence_dir()/'app-source.json').read_text(encoding='utf-8'));current=committed_identity(commit)
 assert current['app_files']==identity['app_files'] and current['sql_files']==identity['sql_files'],'Package app/SQL differs from media source'
 state=json.loads((ROOT/'.local/revision/evaluation.json').read_text(encoding='utf-8'));served=inspect(state,identity)
 browser=json.loads((evidence_dir()/'browser-tests.json').read_text(encoding='utf-8'));recording=json.loads((evidence_dir()/'demo-recording.json').read_text(encoding='utf-8'))
 for doc in [browser,recording]:
  assert doc['result']=='PASS' and doc['deployment_identity']['source_commit']==identity['source_commit'] and doc['deployment_identity']['app_sha256']==identity['app_sha256']
 for name,digest in browser['screenshot_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
 assert sha((ROOT/recording['file']).read_bytes())==recording['sha256']
 files={}
 for row in git('ls-tree','-rz',commit).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t',1);mode,kind,oid=meta.decode().split();name=name.decode();assert kind=='blob'
  assert not name.startswith(('.local/','.git/','dist/')) and not name.endswith('config.local.php') and name!='.env',name
  content=git('cat-file','blob',oid)
  assert (ROOT/name).read_bytes()==content,'Working tree differs: '+name
  files[name]={'sha256':sha(content),'bytes':len(content),'mode':mode,'content':content}
 assert all('sql/'+n in files for n in ['dbcreate.sql','dbinsert.sql','dbdrop.sql','dbdump.sql'])
 assert len(files['README.md']['content'])<15000,'Original private specification must not be packaged'
 metadata=['COMMIT_SHA.txt','RELEASE_MANIFEST.json','VERIFICATION.json']
 manifest={'package_commit':commit,'application_source_commit':identity['source_commit'],'app_sha256':identity['app_sha256'],'built_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'payload_files':{name:{k:v for k,v in d.items() if k!='content'} for name,d in files.items()},'generated_metadata':metadata,'scope':'Committed payload verified separately from actual serving root and application captures; documents may be later than the unchanged application. Review draft; human course upload NOT_RUN.'}
 proof={'result':'PASS','package_commit':commit,'application_source_commit':identity['source_commit'],'app_sha256':identity['app_sha256'],'payload_members':len(files),'payload_matches_commit':True,'working_tree_matches_commit':True,'actual_serving_root_matches':served['served_files']==identity['app_files'],'http_assets_checked':True,'capture_and_recording_app_match':True,'served_url':served['url'],'served_document_root':served['document_root'],'captured_video_sha256':recording['sha256'],'identity_scope':'Every payload member is from package_commit. Actual PHP/CSS/JS/SVG/font bytes and media application match application_source_commit. Full ZIP checksum is external, not self-referential.','course_upload':'NOT_RUN'}
 DIST.mkdir(exist_ok=True);filename='team05-review-2026-11-12-'+commit[:12]+'.zip';target=DIST/filename;pending=DIST/(filename+'.pending')
 with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,d in files.items():
   info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(int(d['mode'],8)&0o777)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,d['content'])
  z.writestr('COMMIT_SHA.txt',commit+'\n');z.writestr('RELEASE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n');z.writestr('VERIFICATION.json',json.dumps(proof,indent=2)+'\n')
 with zipfile.ZipFile(pending) as z:
  assert z.testzip() is None and set(z.namelist())==set(files)|set(metadata)
  for name,d in files.items():assert sha(z.read(name))==d['sha256'],name
  assert z.read('COMMIT_SHA.txt').decode().strip()==commit
 pending.replace(target);proof.update(archive='dist/'+filename,archive_sha256=sha(target.read_bytes()),archive_bytes=target.stat().st_size)
 (DIST/(filename+'.sha256')).write_text(proof['archive_sha256']+'  '+filename+'\n',encoding='utf-8')
 (DIST/(filename+'.verification.json')).write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 alias=DIST/'team05-review-2026-11-12.zip';shutil.copyfile(target,alias)
 (DIST/(alias.name+'.sha256')).write_text(proof['archive_sha256']+'  '+alias.name+'\n',encoding='utf-8')
 (DIST/'revision-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 if a.record_evidence:
  write_evidence('release-verification.json',proof,['python3','tools/package_release.py','--record-evidence'],{'actual_served_url':served['url'],'document_root':served['document_root'],'package_commit':commit},extra=['tools/package_release.py','tools/app_identity.py','tools/review_server.py'])
 print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
