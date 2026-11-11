import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {spawnSync} from 'node:child_process';import crypto from 'node:crypto';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const evidence=path.join(root,'docs/evidence/revision-2026-11-12');
export function appIdentity(){const d=JSON.parse(fs.readFileSync(path.join(evidence,'served-app.json'),'utf8'));if(d.result!=='PASS')throw new Error('Actual served app not verified');return {source_commit:d.source_commit,app_sha256:d.app_sha256,url:d.url,container:d.container,document_root:d.document_root};}
export function verifyDeployment(){const p=spawnSync('python3',['tools/review_server.py','verify'],{cwd:root,encoding:'utf8'});if(p.status!==0)throw new Error(p.stderr+p.stdout);return appIdentity();}
export function sha(file){return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');}
export function writeEvidence(name,data,extras=[],environment={}){
 const command=['node',path.relative(root,process.argv[1])];
 const p=spawnSync('python3',['-c',"import json,sys;sys.path.insert(0,'tools');from evidence_support import write_evidence;d=json.load(sys.stdin);write_evidence(d['name'],d['data'],d['command'],d['environment'],extra=d['extras'])"],{cwd:root,encoding:'utf8',input:JSON.stringify({name,data,command,environment,extras})});
 if(p.status!==0)throw new Error(p.stderr+p.stdout);
}
