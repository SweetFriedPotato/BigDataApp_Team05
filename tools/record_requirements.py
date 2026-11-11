#!/usr/bin/env python3
"""Track implemented requirements without treating draft deliverables as final submission."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=[
('R01','Weather Data Analysis scope','team05/index.php','data-validation.md','PASS'),
('R02','Six-table create SQL, PK/FK/indexes','sql/dbcreate.sql','evidence/schema.json','PASS'),
('R03','Plain INSERT seed before analysis','sql/dbinsert.sql','evidence/data-validation.json','PASS'),
('R04','Project-only child-first DROP and reset','sql/dbdrop.sql','evidence/clean-install.json','PASS'),
('R05','Actual mysqldump and dump-only restore','sql/dbdump.sql','evidence/clean-install.json','PASS'),
('R06','Web INSERT','team05/plan_actions.php','evidence/plans-http.json','PASS'),
('R07','Web SELECT list/detail','team05/plan_detail.php','evidence/plans-http.json','PASS'),
('R08','Web UPDATE body and selected locations','team05/includes/plans.php','evidence/plans-tests.json','PASS'),
('R09','Web DELETE with cascading children','team05/plans.php','evidence/plans-tests.json','PASS'),
('R10','Complex grouping over multiple dimensions','team05/aggregate.php','evidence/aggregate-tests.json','PASS'),
('R11','OLAP drilldown/up and SQL WITH ROLLUP','team05/olap.php','evidence/olap-tests.json','PASS'),
('R12','Dense ranking, full rates and Top N ties','team05/ranking.php','evidence/ranking-tests.json','PASS'),
('R13','Continuous 7/30 day windowing','team05/window.php','evidence/window-tests.json','PASS'),
('R14','Four separate menus and analysis URLs','team05/includes/header.php','evidence/browser-tests.json','PASS'),
('R15','Validated dynamic user inputs and native PDO binding','team05/includes/queries.php','evidence/prepared-queries.json','PASS'),
('R16','Date/number/check/select/buttons','team05/includes/view.php','evidence/browser-tests.json','PASS'),
('R17','PHP Session retains conditions across pages','team05/includes/session.php','evidence/common-http.json','PASS'),
('R18','Successful COMMIT and actual intermediate-failure ROLLBACK','team05/includes/plans.php','evidence/plans-tests.json','PASS'),
('R19','Central config and checked local override','team05/config.php','evidence/clean-install.json','PASS'),
('R20','team05 DB/user/password; no root app connection','team05/config.php','evidence/schema.json','PASS'),
('R21','Install exactly under htdocs/team05','team05/index.php','evidence/xampp-install.json','TODO'),
('R22','Fresh XAMPP from PHP+SQL with no API/CDN','tools/verify_xampp.py','evidence/xampp-install.json','TODO'),
('R23','Demo source and packaged commit match','tools/package_release.py','evidence/release-verification.json','TODO'),
('R24','At least five base tables; actual six','sql/dbcreate.sql','evidence/schema.json','PASS'),
('R25','At least five user screens; actual nine','team05/includes/header.php','evidence/browser-tests.json','PASS'),
('R26','Implementation report final rendered minimum 10 pages','docs/report.md','evidence/document-render.json','TODO'),
('R27','English paper final rendered minimum 4 pages','docs/paper.md','evidence/document-render.json','TODO'),
('R28','ERD/PHP structure/code/schedule/contributions','docs/report.md','report.md','TODO'),
('R29','English PPT, oral presentation and backup video','docs/demo-script.md','demo-script.md','TODO'),
('R30','Actual individual contributions and author comments','docs/contributions.md','contributions.md','BLOCKED'),
]
lines=['# Requirements traceability','',
'PASS records executed implementation evidence. Draft documentation is distinguished from final reviewed course deliverables. The original local specification is preserved under `.local/` and is not uploaded.','',
'| ID | Requirement | Status | Implementation | Actual evidence | Implementation commit |','|---|---|---|---|---|---|']
for id,description,file,proof,status in items:
    evidence=ROOT/'docs'/proof
    note=''
    if id in ('R21','R22') and evidence.exists():
        result=json.loads(evidence.read_text())['result'];status='PASS' if result=='PASS' else 'FAIL';note=' (actual Linux XAMPP; professor Windows host NOT_RUN)'
    if id=='R23' and evidence.exists():status=json.loads(evidence.read_text())['result']
    if id in ('R26','R27') and evidence.exists():
        render=json.loads(evidence.read_text());kind='report' if id=='R26' else 'paper';pages=render[kind]['pages'];minimum=10 if id=='R26' else 4
        status='PASS' if pages>=minimum else 'FAIL';note=f' (draft PDF {pages} pages; final human review pending)'
    if id=='R28' and (ROOT/'docs/erd.mmd').exists() and (ROOT/'docs/php-structure.mmd').exists() and (ROOT/file).exists():status='PASS';note=' (draft report records all sections; actual human contribution information remains pending)'
    if id=='R29':note=' (English draft/script prepared in P9; final oral presentation and submitted backup video NOT_RUN)'
    if id=='R30':note=' (Codex implementation is recorded honestly; team members must supply their actual roles/effort)'
    log=subprocess.run(['git','log','-1','--format=%h','--',file],cwd=ROOT,capture_output=True,text=True).stdout.strip() or 'pending document milestone'
    link='['+file+']('+('../'+file if not file.startswith('docs/') else file[5:])+')'
    lines.append(f'| {id} | {description}{note} | **{status}** | {link} | [evidence]({proof}) | {log} |')
lines+=['','Scope note: NASA retrieval was performed here; KASI/RDA values came from the user-provided verified appendix snapshots. No new final almanac cross-check or RDA full-page download is claimed.','',
'Commits use the existing configured Git identity. They record the Codex-assisted process and do not establish personal human authorship. GitHub HTTPS push is blocked by absent credentials; see progress.md and evidence/git-status.json.']
(ROOT/'docs/requirements.md').write_text('\n'.join(lines)+'\n')
print('Recorded 30 requirements with actual evidence and final-review limits')
