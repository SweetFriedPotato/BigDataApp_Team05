#!/usr/bin/env python3
"""Verify assignment consistency, never infer completed human work."""
import json
from evidence_support import ROOT,write_evidence

def verify():
    data=json.loads((ROOT/'tools/team-responsibilities.json').read_text(encoding='utf-8'));members=data['members']
    assert {m['id'] for m in members}=={'2371001','2376329','2376274','2476009','2276337'}
    for area in ['technical_share','report_share','paper_share','presentation_share']:
        assert sum(m[area] for m in members)==100 and all(m[area]==20 for m in members)
    assert sorted(s for m in members for s in m['slides'])==list(range(2,12))
    checked=[]
    for m in members:
        marker=f"Team responsibility: {m['name']} ({m['id']})"
        for file in m['code_paths']:
            assert marker in (ROOT/file).read_text(encoding='utf-8'),file;checked.append(file)
    for doc in ['docs/team-responsibilities.md','docs/contributions.md']:
        text=(ROOT/doc).read_text(encoding='utf-8')
        assert all(m['id'] in text and m['name'] in text for m in members)
        assert '20%' in text and 'NOT_RUN' in text
        if doc.endswith('contributions.md'):
            assigned=text.split('## Confirmed assignment')[1].split('## Actual execution')[0]
            assert all(m['id'] in assigned for m in members)
    human=json.loads((ROOT/'docs/human-review.json').read_text(encoding='utf-8'))
    result={'result':'PASS','equal_responsibilities':True,'members':members,'source_comments_checked':checked,'shared_work':data['shared_work'],'actual_member_review_status':human['member_reviews']['status'],'actual_oral_status':human['oral_presentation']['status']}
    write_evidence('responsibilities.json',result,['python3','tools/check_responsibilities.py'],extra=['tools/check_responsibilities.py','tools/team-responsibilities.json','docs/team-responsibilities.md','docs/contributions.md','docs/human-review.json'])
    return result
if __name__=='__main__':print(json.dumps({'result':verify()['result'],'scope':'Assignment and code labels only; human completion remains separate'}))
