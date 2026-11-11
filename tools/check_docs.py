#!/usr/bin/env python3
"""Check local Markdown link destinations; optional one-time pending release evidence exception."""
import json,re,subprocess,sys
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
files=subprocess.check_output(['rg','--files','-g','*.md'],cwd=ROOT,text=True).splitlines()
checked=0;missing=[];pending=[]
for name in files:
    content=(ROOT/name).read_text(encoding='utf-8')
    for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)',content):
        target=target.strip('<>');parts=urlsplit(target)
        if parts.scheme or not parts.path:continue
        path=((ROOT/name).parent/unquote(parts.path)).resolve();checked+=1
        if not path.exists():
            if '--allow-pending-release' in sys.argv and path==ROOT/'docs/evidence/release-verification.json':pending.append(str(path))
            else:missing.append({'document':name,'target':target})
if missing:raise RuntimeError(json.dumps(missing,indent=2))
if pending:print(f'{checked} local links checked; only release proof pending packaging');sys.exit(0)
result={'result':'PASS','markdown_files':len(files),'local_link_targets_checked':checked,'missing':[],'external_links':'Source URLs retained; availability not retested by this local-link check'}
(ROOT/'docs/evidence/document-links.json').write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8');print(json.dumps(result,indent=2))
