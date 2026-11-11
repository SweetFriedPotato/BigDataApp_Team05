#!/usr/bin/env python3
"""Package exactly a clean committed tree, verify every member and current demo code.
Metadata is generated outside Git to avoid embedding a commit's own hash in that commit.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist';DIST.mkdir(exist_ok=True)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    dirty=git('status','--porcelain','--untracked-files=normal').decode().strip()
    if dirty:raise RuntimeError('Commit/review all changes before packaging; tree must be clean: '+dirty[:1500])
    commit=git('rev-parse','HEAD').decode().strip()
    tree=git('ls-tree','-rz',commit)
    files={}
    for row in tree.split(b'\x00'):
        if not row:continue
        meta,name=row.split(b'\t',1);mode,kind,object_id=meta.decode().split();name=name.decode()
        if kind!='blob':raise RuntimeError('Unsupported tree member')
        if name.startswith(('.local/','.git/','dist/')) or name.endswith('config.local.php') or name=='.env':raise RuntimeError('Private file unexpectedly tracked: '+name)
        content=git('cat-file','blob',object_id)
        files[name]={'sha256':sha(content),'bytes':len(content),'mode':mode,'content':content}
    assert all('sql/'+x in files for x in ('dbcreate.sql','dbinsert.sql','dbdrop.sql','dbdump.sql'))
    assert 'README.md' in files and len(files['README.md']['content'])<15000,'Original specification must not be packaged'
    for name,item in files.items():
        if name.startswith(('team05/','sql/')):
            assert (ROOT/name).is_file() and sha((ROOT/name).read_bytes())==item['sha256'],'Live demo differs from commit: '+name
    manifest={'source_commit':commit,'built_at_utc':datetime.now(timezone.utc).isoformat(),
              'payload_files':{name:{k:v for k,v in item.items() if k!='content'} for name,item in files.items()},
              'generated_metadata':['COMMIT_SHA.txt','RELEASE_MANIFEST.json','VERIFICATION.json'],
              'scope':'review draft; not a final course upload; no personal contribution assertions'}
    pending=DIST/'team05-review.pending.zip';target=DIST/'team05-review.zip'
    with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,item in files.items():
            info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(int(item['mode'],8)&0o777)<<16;info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,item['content'])
        z.writestr('COMMIT_SHA.txt',commit+'\n');z.writestr('RELEASE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(pending) as z:
        assert set(z.namelist())==set(files)|{'COMMIT_SHA.txt','RELEASE_MANIFEST.json'}
        for name,item in files.items():assert sha(z.read(name))==item['sha256'],name
        assert z.read('COMMIT_SHA.txt').decode().strip()==commit
    proof={'result':'PASS','source_commit':commit,'payload_members':len(files),
           'payload_check':'Every archive payload byte matches the selected Git commit',
           'demo_check':'Every current team05/ and sql/ file byte matches the same commit',
           'metadata':'Only three declared identity/verification files are generated outside the committed payload',
           'draft':True}
    with zipfile.ZipFile(pending,'a',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('VERIFICATION.json',json.dumps(proof,indent=2)+'\n')
    with zipfile.ZipFile(pending) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(files)|set(manifest['generated_metadata'])
        for name,item in files.items():assert sha(z.read(name))==item['sha256'],name
    pending.replace(target)
    proof['archive']='dist/team05-review.zip';proof['archive_sha256']=sha(target.read_bytes());proof['archive_bytes']=target.stat().st_size
    (DIST/'review-verification.json').write_text(json.dumps(proof,indent=2)+'\n', encoding='utf-8')
    (DIST/'team05-review.zip.sha256').write_text(proof['archive_sha256']+'  team05-review.zip\n', encoding='utf-8')
    # Stable evidence points to the concrete per-release proof; contains no self-referential commit hash.
    stable={'result':'PASS','test_id':'T34','check':'Archive payload and live demo PHP/SQL match one committed source byte for byte',
            'current_release_identity':'COMMIT_SHA.txt and RELEASE_MANIFEST.json inside the review ZIP',
            'concrete_proof':'VERIFICATION.json inside ZIP; dist/review-verification.json and SHA-256 sidecar in the local workspace',
            'command':'python3 tools/package_release.py','scope':'review package only; actual course submission NOT_RUN'}
    (ROOT/'docs/evidence/release-verification.json').write_text(json.dumps(stable,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
