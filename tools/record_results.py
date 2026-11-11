#!/usr/bin/env python3
"""Generate test statuses from actual evidence, preserving execution provenance."""
import argparse,json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from evidence_support import ROOT,evidence_dir
from evidence_status import Store,data_checks,schema_checks,field
CONTRACTS=json.loads((ROOT/'tools/test-contracts.json').read_text(encoding='utf-8'))
SUITES={'aggregate':range(5,9),'olap':range(9,11),'ranking':range(11,14),'window':range(14,19),'plans':range(21,26),'seasonal':[3,28]}
def collect(store):
    rows={}
    def add(id,file,validator=None,**kw):rows[id]=store.result(file,validator,**kw)
    add('T01','data-validation.json',lambda d:data_checks(d))
    add('T02','data-validation.json',lambda d:data_checks(d,True))
    add('T04','schema.json',schema_checks)
    for suite,ids in SUITES.items():
        for n in ids:add(f'T{n:02d}',suite+'-tests.json',test_id=f'T{n:02d}')
    add('T19','common-http.json',lambda d:[('Session result',None if 'session' not in d else bool(d['session']))])
    add('T20','common-http.json',lambda d:[('invalid cases actually tested',None if 'invalid_cases' not in d else isinstance(d['invalid_cases'],int) and d['invalid_cases']>=13)])
    for n in (26,27):add(f'T{n}','plans-http.json',lambda d,n=n:[('actual HTTP check',None if f'T{n}' not in d else bool(d[f'T{n}']))])
    for n in (29,30,31,32,33):
        validator=None
        if n==32:
            def validator(d):
                a=d.get('actual',{});return [('internal network inspected',field(a,'internal_network',True)),('network count',None if 'attached_networks' not in a else len(a['attached_networks'])==1),('public egress rejected',None if 'public_request_exit' not in a else isinstance(a['public_request_exit'],int) and a['public_request_exit']>0)]
        add(f'T{n}','clean-install.json',validator,step=f'T{n} ')
    add('T34','release-verification.json',lambda d:[('ZIP/working tree comparison',field(d,'payload_matches_commit',True)),('working tree comparison',field(d,'working_tree_matches_commit',True))])
    for n in (35,36,37,38):add(f'T{n}','revision-functional.json',test_id=f'T{n}')
    add('T39','evidence-regression.json',lambda d:[('normal/failure/missing fixtures',field(d,'fixture_classes',['normal','failing','missing'])),('strict failure exits',field(d,'strict_exit_verified',True))])
    add('T40','utf8-seed.json',lambda d:[('same seed body',field(d,'seed_content_unchanged',True)),('same data files',field(d,'data_files_unchanged',True)),('UTF-8 operations explicit',field(d,'explicit_utf8',True))])
    add('T41','chart-tests.json',test_id='T41')
    add('T42','deployment-media.json',lambda d:[('served files match package app',field(d,'served_files_match',True)),('capture files match same app',field(d,'capture_manifest_matches',True)),('recorded app identity',field(d,'recording_manifest_matches',True)),('source commit',None if 'source_commit' not in d else isinstance(d['source_commit'],str) and len(d['source_commit'])==40)])
    add('T43','browser-tests.json',lambda d:[('all nine routes',field(d,'user_screen_count',9)),('viewports',None if 'viewports' not in d else set(d['viewports'])>={'1440x900','1366x768','390x844','360x844'}),('no console errors',field(d,'console_errors',[])),('no external runtime requests',field(d,'external_runtime_requests',[])),('no page overflow',field(d,'document_overflow',[])),('keyboard and no-JS checks',field(d,'keyboard_and_no_js',True))])
    add('T44','submission-docs.json',lambda d:[('report pages',None if 'report_pages' not in d else d['report_pages']>=10),('paper pages',None if 'paper_pages' not in d else d['paper_pages']>=4),('PPT actually rendered',field(d,'ppt_rendered_pages',12)),('no slide overlaps',field(d,'overlaps',[])),('actual source excerpts',field(d,'source_excerpts_match',True)),('20% responsibility matrix',field(d,'equal_responsibilities',True)),('all slides visually reviewed',field(d,'visual_reviewed_slides',list(range(1,13))))])
    return rows

def render(rows,store):
    now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
    lines=['# Actual test results','',f'Matrix generated {now}. This is **not** the time the tests were run. Execution dates, commands, environments and input file hashes are retained in each linked JSON. Historical 2026-11-11 evidence remains in its original paths.','',
        'Statuses: PASS = complete current evidence; FAIL = observed mismatch/failure; PARTIAL = incomplete/stale evidence; NOT_RUN = absent execution; BLOCKED = explicit external obstacle.','',
        '| ID | Expected check | Result | Actual evidence | Execution / command / input identity |','|---|---|---|---|---|']
    for id,row in sorted(rows.items()):
        path=store.directory/row['evidence']
        try:relative=path.relative_to(ROOT/'docs')
        except ValueError:relative=path
        actual=json.dumps(row['actual'],ensure_ascii=False) if not isinstance(row['actual'],str) else row['actual']
        actual=actual.replace('|','/').replace('\n',' ')[:600]
        meta=row.get('execution') or {}
        provenance=f"{meta.get('executed_at','Not recorded')} · {meta.get('command','Not recorded')} · {len(meta.get('source_files',{}))} input hashes"
        notes='; '.join(row.get('notes',[]))
        lines.append(f"| {id} | {CONTRACTS.get(id,id)} | **{row['status']}** | {actual} {notes} [JSON]({relative}) | {str(provenance).replace('|','/')} |")
    lines += ['','Human oral presentation, actual member review/sign-off and course upload have not been performed by these technical tests. Linux/XAMPP results do not establish Windows/macOS or professor-host results.']
    return '\n'.join(lines)+'\n'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path,default=evidence_dir());parser.add_argument('--output',type=Path,default=ROOT/'docs/test-results.md');parser.add_argument('--json-output',type=Path);parser.add_argument('--ids',nargs='+');parser.add_argument('--fail-on-error',action='store_true');args=parser.parse_args()
    store=Store(ROOT,args.evidence_dir);rows=collect(store)
    if args.ids:rows={id:rows[id] for id in args.ids}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(render(rows,store),encoding='utf-8')
    if args.json_output:args.json_output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={state:sum(r['status']==state for r in rows.values()) for state in ('PASS','FAIL','PARTIAL','NOT_RUN','BLOCKED')}
    print(json.dumps({'test_rows':len(rows),'statuses':counts,'matrix_generation_only':True}))
    return 1 if args.fail_on_error and any(r['status']!='PASS' for r in rows.values()) else 0
if __name__=='__main__':raise SystemExit(main())
