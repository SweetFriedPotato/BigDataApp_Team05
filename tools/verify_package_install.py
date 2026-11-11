#!/usr/bin/env python3
"""Extract the supplied archive outside Git and run its own XAMPP checks in a fresh DB."""
import argparse,hashlib,json,subprocess,tempfile,zipfile
from pathlib import Path
from evidence_support import ROOT,evidence_dir,metadata
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,default=evidence_dir()/'package-install.json');a=p.parse_args();archive=a.archive.resolve()
result={'archive':str(archive.relative_to(ROOT)) if archive.is_relative_to(ROOT) else str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
try:
 with tempfile.TemporaryDirectory(prefix='slg-delivered-',dir='/tmp') as tmp:
  source=Path(tmp)
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   for name in z.namelist():assert (source/name).resolve().is_relative_to(source)
   manifest=json.loads(z.read('RELEASE_MANIFEST.json'));commit=z.read('COMMIT_SHA.txt').decode().strip();assert commit==manifest['package_commit']
   for name,row in manifest['payload_files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==row['sha256'],name
   z.extractall(source)
  assert not (source/'.git').exists() and not (source/'.local').exists()
  check=subprocess.run(['python3','tools/verify_xampp.py'],cwd=source,text=True,capture_output=True,encoding='utf-8')
  inner=json.loads((source/'docs/evidence/revision-2026-11-12/xampp-install.json').read_text(encoding='utf-8'))
  assert check.returncode==0 and inner['result']=='PASS',check.stdout+check.stderr
  assert any(s['actual'].get('docker_network_mode')=='none' for s in inner['steps'])
  result.update(result='PASS',package_commit=commit,application_source_commit=manifest['application_source_commit'],app_sha256=manifest['app_sha256'],payload_members_verified=len(manifest['payload_files']),extraction_outside_git=True,source='Only archive payload; no original workspace mounted into XAMPP',inner_command=['python3','tools/verify_xampp.py'],inner_output=check.stdout,inner_evidence=inner,scope='Actual delivered PHP/SQL + bundled tests from clean extraction; fresh official XAMPP, all nine screens/CRUD, SQL suites, reset/dump restore and no-network mode; professor physical host NOT_RUN')
except Exception as e:result.update(result='FAIL',error=str(e));raise
finally:
 result['_meta']=metadata(['python3','tools/verify_package_install.py','--archive',result['archive']],{'outer':'isolated /tmp extraction','inner':'official Linux XAMPP network=none'},extra=['tools/verify_package_install.py','tools/verify_xampp.py'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='inner_evidence' and k!='_meta'},indent=2))
