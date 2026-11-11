#!/usr/bin/env python3
"""Observe public Git refs; never read credential files or expose tokens."""
import json,subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from evidence_support import evidence_dir

def git(*args):return subprocess.check_output(['git',*args],text=True,encoding='utf-8').strip()
local=git('rev-parse','HEAD');refs={}
for line in git('ls-remote','origin','refs/heads/main','refs/tags/review-2026-11-11','refs/tags/review-2026-11-11^{}').splitlines():
 sha,name=line.split();refs[name]=sha
remote=refs.get('refs/heads/main');review=refs.get('refs/tags/review-2026-11-11^{}') or refs.get('refs/tags/review-2026-11-11')
result={'status':'SYNCHRONIZED' if remote==local else 'LOCAL_CHANGES_NOT_YET_PUSHED','checked_at':datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),'local_head':local,'remote_main':remote,'existing_review_tag':review,'review_tag_preserved':review=='7c7c8509266f38d02f49965ee89f2bef0d53619a','remote_url':git('remote','get-url','origin'),'scope':'A snapshot of observed refs at checked_at; later commits may advance main. Earlier auth failures remain historical.'}
assert result['review_tag_preserved'],'Existing review tag changed unexpectedly'
path=evidence_dir();path.mkdir(parents=True,exist_ok=True);(path/'git-status.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
