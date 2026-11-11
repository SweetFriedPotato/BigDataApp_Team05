#!/usr/bin/env python3
"""Requirement judgments combine their full evidence scope, never hardcoded PASSs."""
import argparse,json,subprocess
from pathlib import Path
from evidence_support import ROOT,evidence_dir
from evidence_status import Store,combine,field
from record_results import collect
ITEMS={
'R01':('Weather Data Analysis scope','team05/index.php',['T01','T02']),
'R02':('Six-table DDL with keys and indexes','sql/dbcreate.sql',['T04']),
'R03':('Deterministic plain INSERT seed','sql/dbinsert.sql',['T01','T02','T03','T40']),
'R04':('Project-only DROP and reinitialization','sql/dbdrop.sql',['T30']),
'R05':('Actual DB dump and dump-only restore','sql/dbdump.sql',['T31']),
'R06':('Web INSERT','team05/plan_actions.php',['T21','T27']),
'R07':('Web SELECT/list/detail','team05/plan_detail.php',['T21','T27']),
'R08':('Web UPDATE including selected locations/timestamp','team05/includes/plans.php',['T22','T27','T35']),
'R09':('Web DELETE and cascading children','team05/plans.php',['T23','T27']),
'R10':('Complex grouping and weighted valid-day statistics','team05/aggregate.php',['T05','T06','T07','T08']),
'R11':('OLAP hierarchy and WITH ROLLUP','team05/olap.php',['T09','T10']),
'R12':('Dense ranks, ties and Top N ranks','team05/ranking.php',['T11','T12','T13']),
'R13':('Continuous SQL 7/30-day windows','team05/window.php',['T14','T15','T16','T17','T18','T41']),
'R14':('Four separate menus and URLs','team05/includes/header.php',['T43']),
'R15':('Validated dynamic inputs and native prepared statements','team05/includes/queries.php',['T05','T09','T13','T16','T20']),
'R16':('Dates, numbers, checkbox, select and buttons','team05/includes/view.php',['T43']),
'R17':('PHP Session shared comparison conditions','team05/includes/session.php',['T19','T26','T37','T38']),
'R18':('Real COMMIT and intermediate-failure rollback','team05/includes/plans.php',['T21','T24','T25','T35']),
'R19':('Central configuration with local override','team05/config.php',['T33']),
'R20':('team05 DB and non-root evaluation account','team05/config.php',['T04','T33']),
'R21':('Actual htdocs/team05 installation','tools/verify_xampp.py',['T33']),
'R22':('Fresh offline installation from supplied PHP/SQL','tools/verify_xampp.py',['T29','T30','T31','T32']),
'R23':('Package, actual serving root and recorded app identity','tools/package_release.py',['T34','T42']),
'R24':('At least five base tables; actual six','sql/dbcreate.sql',['T04']),
'R25':('At least five user screens; actual nine','team05/includes/header.php',['T43']),
'R26':('Rendered report minimum 10 pages (review draft)','docs/report.md',['T44']),
'R27':('Rendered English paper minimum 4 pages (review draft)','docs/paper.md',['T44']),
'R28':('ERD, PHP structure, actual code, schedule and personal work evidence','docs/report.md',['T44']),
'R29':('English PPT, actual oral presentation and backup video','docs/demo-script.md',['T42','T44']),
'R30':('Equal assigned responsibility, name comments and actual member review','docs/contributions.md',['T44'])}
def collect_requirements(store):
    tests=collect(store);out={}
    for id,(description,file,ids) in ITEMS.items():
        checks=[tests[t]['status'] for t in ids];notes=[]
        if not (ROOT/file).is_file():checks.append('NOT_RUN');notes.append('Required implementation/source file absent')
        if id in ('R06','R07','R08','R09'):
            proof=store.result('plans-http.json');checks.append(proof['status'])
        if id in ('R21','R22'):
            proof=store.result('xampp-install.json',lambda d:[('actual XAMPP network none',None if 'steps' not in d else any(x.get('status')=='PASS' and x.get('actual',{}).get('docker_network_mode')=='none' for x in d['steps']))]);checks.append(proof['status']);notes.append('Actual tested OS only; professor physical host NOT_RUN')
        if id in ('R28','R29','R30'):
            document=store.result('submission-docs.json',lambda d:[('all required report features',None if 'report_features' not in d else all(d['report_features'].get(k) is True for k in ['erd','php_structure','ddl_keys_indexes','seed_drop','pdo','session','crud','transaction','input_controls','four_analyses','timeline','responsibility_results']))])
            checks.append(document['status'])
            human_path=ROOT/'docs/human-review.json'
            human=json.loads(human_path.read_text(encoding='utf-8')) if human_path.exists() else {}
            key='oral_presentation' if id=='R29' else 'member_reviews'
            actual=human.get(key,{'status':'NOT_RUN'})
            human_status=actual.get('status','NOT_RUN')
            if human_status!='PASS':checks.append(human_status if human_status in ('NOT_RUN','PARTIAL','FAIL','BLOCKED') else 'PARTIAL')
            notes.append('Assigned 20% responsibility is separate from actual human completion; '+key+'='+human_status)
        status=combine(checks)
        out[id]={'description':description,'status':status,'implementation':file,'tests':ids,'notes':notes}
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-dir',type=Path,default=evidence_dir());parser.add_argument('--output',type=Path,default=ROOT/'docs/requirements.md');parser.add_argument('--json-output',type=Path);parser.add_argument('--ids',nargs='+');parser.add_argument('--fail-on-error',action='store_true');a=parser.parse_args()
    rows=collect_requirements(Store(ROOT,a.evidence_dir))
    if a.ids:rows={id:rows[id] for id in a.ids}
    lines=['# Requirements traceability','', 'Current judgments are derived from executed test evidence and complete requirement scope. PARTIAL does not mean a failed SQL calculation; it can identify a pending human review or an artifact not yet verified. The generation time is not a test execution time.','', '| ID | Requirement | Status | Implementation | Mapped evidence / remaining scope |','|---|---|---|---|---|']
    for id,r in rows.items():
        path=r['implementation'];target=path[5:] if path.startswith('docs/') else '../'+path
        lines.append(f"| {id} | {r['description']} | **{r['status']}** | [{path}]({target}) | {', '.join(r['tests'])}; {'; '.join(r['notes'])} |")
    git_path=a.evidence_dir/'git-status.json'
    git=json.loads(git_path.read_text(encoding='utf-8')) if git_path.exists() else {}
    lines+=['', 'Git synchronization: '+json.dumps({k:git.get(k,'NOT_RUN') for k in ['status','checked_at','local_head','remote_main','existing_review_tag']},ensure_ascii=False)+'. Historical authentication failures are retained in progress.md; current status comes from this observed snapshot.', '', 'KASI/RDA use the supplied reference snapshots; no new official-almanac cross-check is claimed. Windows/macOS, professor-host execution, real member sign-off, actual oral presentation and course upload are not inferred from Linux technical tests.']
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    if a.json_output:a.json_output.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'requirements':len(rows),'statuses':{s:sum(r['status']==s for r in rows.values()) for s in ('PASS','FAIL','PARTIAL','NOT_RUN','BLOCKED')}}))
    return 1 if a.fail_on_error and any(r['status']!='PASS' for r in rows.values()) else 0
if __name__=='__main__':raise SystemExit(main())
