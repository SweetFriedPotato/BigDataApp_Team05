#!/usr/bin/env python3
"""Separate immutable application identity from later document/package commits."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from evidence_support import ROOT,evidence_dir

def canonical_hash(mapping):return hashlib.sha256(json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def committed_identity(commit):
    commit=subprocess.check_output(['git','rev-parse',commit],cwd=ROOT,text=True).strip();app={};sql={}
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','team05','sql'],cwd=ROOT,text=True).splitlines()
    for name in names:
        data=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT);digest=hashlib.sha256(data).hexdigest()
        if name.startswith('team05/'):app[name[7:]]=digest
        else:sql[name]=digest
    return {'source_commit':commit,'app_sha256':canonical_hash(app),'app_files':app,'sql_files':sql,'identity_scope':'Application file bytes only; generated documents and evidence are outside this identity'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--commit',default='HEAD');p.add_argument('--output',type=Path,default=evidence_dir()/'app-source.json');a=p.parse_args()
    identity=committed_identity(a.commit)
    for name,digest in identity['app_files'].items():assert hashlib.sha256((ROOT/'team05'/name).read_bytes()).hexdigest()==digest,name
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8');print(identity['source_commit'],identity['app_sha256'])
if __name__=='__main__':main()
