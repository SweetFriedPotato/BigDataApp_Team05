#!/usr/bin/env python3
"""Bind actual serving files, committed ZIP application bytes and captured artifacts."""
import json,zipfile,hashlib
from evidence_support import ROOT,evidence_dir,digest,write_evidence
from review_server import inspect
D=evidence_dir()
identity=json.loads((D/'app-source.json').read_text(encoding='utf-8'));state=json.loads((ROOT/'.local/revision/evaluation.json').read_text(encoding='utf-8'))
served=inspect(state,identity)
with zipfile.ZipFile(state['archive']) as z:
 for name,expected in identity['app_files'].items():assert hashlib.sha256(z.read('team05/'+name)).hexdigest()==expected,name
 for name,expected in identity['sql_files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==expected,name
browser=json.loads((D/'browser-tests.json').read_text(encoding='utf-8'));figures=json.loads((D/'figure-capture.json').read_text(encoding='utf-8'));video=json.loads((D/'demo-recording.json').read_text(encoding='utf-8'))
for document in [browser,figures,video]:
 assert document['result']=='PASS'
 d=document['deployment_identity'];assert d['source_commit']==identity['source_commit'] and d['app_sha256']==identity['app_sha256'] and d['url']==served['url']
for name,expected in browser['screenshot_sha256'].items():assert digest(ROOT/name)==expected,name
for figure in figures['figures']:assert digest(ROOT/figure['file'])==figure['sha256']
assert digest(ROOT/video['file'])==video['sha256'] and video['duration_seconds']>=200 and video['resolution']=='1440x900' and video['test_plan']=='deleted'
result={'result':'PASS','source_commit':identity['source_commit'],'app_sha256':identity['app_sha256'],'served_files_match':True,'capture_manifest_matches':True,'recording_manifest_matches':True,'committed_zip_application_match':True,'deployed_zip_sha256':digest(state['archive']),'actual_document_root':served['document_root'],'actual_url':served['url'],'actual_container':served['container'],'screenshots':len(browser['screenshot_sha256']),'figure_count':len(figures['figures']),'video_seconds':video['duration_seconds'],'video_resolution':video['resolution'],'video_sha256':video['sha256'],'video_frame_review':'Codex inspected decoded frames at 35, 185 and 245 seconds; caption readability and actual before-Apply form / region-only timestamp / closing source identity checked','scope':'Committed application ZIP → actual serving-container PHP/CSS/JS/SVG/font hashes + HTTP assets → captured application. Final later documentation/package commit is separately verified by tools/package_release.py; app manifest must remain identical.','human_oral_delivery':'NOT_RUN'}
write_evidence('deployment-media.json',result,['python3','tools/verify_media.py'],{'url':served['url'],'container':served['container'],'document_root':served['document_root']},extra=['tools/verify_media.py','tools/review_server.py','tools/app_identity.py','docs/evidence/revision-2026-11-12/app-source.json','docs/evidence/revision-2026-11-12/browser-tests.json','docs/evidence/revision-2026-11-12/figure-capture.json','docs/evidence/revision-2026-11-12/demo-recording.json'])
print(json.dumps(result,indent=2))
