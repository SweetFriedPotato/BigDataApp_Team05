"""Executed-evidence provenance. Output hashes never include the evidence file itself."""
import hashlib,json,os,platform,subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE=ROOT/'docs/evidence/revision-2026-11-12'
def evidence_dir():return Path(os.environ.get('SLG_EVIDENCE_DIR',str(DEFAULT_EVIDENCE))).resolve()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source_manifest(group='app',extra=()):
    folders=('team05','sql') if group=='app' else ('data',)
    paths=[p for folder in folders for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='config.local.php']
    paths += [ROOT/p for p in extra]
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths)) if p.is_file()}
def metadata(command,environment=None,group='app',extra=()):
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True)
    return {'executed_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'command':command,
        'environment':environment or {'platform':platform.platform(),'python':platform.python_version()},
        'source_commit_base':git.stdout.strip() if git.returncode==0 else None,
        'source_files':source_manifest(group,extra),'identity_scope':'File hashes identify executed inputs, including uncommitted changes; this evidence does not hash itself.'}
def write_evidence(name,document,command,environment=None,group='app',extra=()):
    directory=evidence_dir();directory.mkdir(parents=True,exist_ok=True)
    doc=dict(document);doc['_meta']=metadata(command,environment,group,extra)
    (directory/name).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return doc
