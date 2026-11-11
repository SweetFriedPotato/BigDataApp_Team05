# Requirements traceability

PASS records executed implementation evidence. Draft documentation is distinguished from final reviewed course deliverables. The original local specification is preserved under `.local/` and is not uploaded.

| ID | Requirement | Status | Implementation | Actual evidence | Implementation commit |
|---|---|---|---|---|---|
| R01 | Weather Data Analysis scope | **PASS** | [team05/index.php](../team05/index.php) | [evidence](data-validation.md) | 4198842 |
| R02 | Six-table create SQL, PK/FK/indexes | **PASS** | [sql/dbcreate.sql](../sql/dbcreate.sql) | [evidence](evidence/schema.json) | e660795 |
| R03 | Plain INSERT seed before analysis | **PASS** | [sql/dbinsert.sql](../sql/dbinsert.sql) | [evidence](evidence/data-validation.json) | c9ff724 |
| R04 | Project-only child-first DROP and reset | **PASS** | [sql/dbdrop.sql](../sql/dbdrop.sql) | [evidence](evidence/clean-install.json) | e660795 |
| R05 | Actual mysqldump and dump-only restore | **PASS** | [sql/dbdump.sql](../sql/dbdump.sql) | [evidence](evidence/clean-install.json) | cb2ce62 |
| R06 | Web INSERT | **PASS** | [team05/plan_actions.php](../team05/plan_actions.php) | [evidence](evidence/plans-http.json) | fba9c9f |
| R07 | Web SELECT list/detail | **PASS** | [team05/plan_detail.php](../team05/plan_detail.php) | [evidence](evidence/plans-http.json) | fba9c9f |
| R08 | Web UPDATE body and selected locations | **PASS** | [team05/includes/plans.php](../team05/includes/plans.php) | [evidence](evidence/plans-tests.json) | fba9c9f |
| R09 | Web DELETE with cascading children | **PASS** | [team05/plans.php](../team05/plans.php) | [evidence](evidence/plans-tests.json) | fba9c9f |
| R10 | Complex grouping over multiple dimensions | **PASS** | [team05/aggregate.php](../team05/aggregate.php) | [evidence](evidence/aggregate-tests.json) | d7b7b15 |
| R11 | OLAP drilldown/up and SQL WITH ROLLUP | **PASS** | [team05/olap.php](../team05/olap.php) | [evidence](evidence/olap-tests.json) | 932d1d0 |
| R12 | Dense ranking, full rates and Top N ties | **PASS** | [team05/ranking.php](../team05/ranking.php) | [evidence](evidence/ranking-tests.json) | 71340b0 |
| R13 | Continuous 7/30 day windowing | **PASS** | [team05/window.php](../team05/window.php) | [evidence](evidence/window-tests.json) | 0e7e894 |
| R14 | Four separate menus and analysis URLs | **PASS** | [team05/includes/header.php](../team05/includes/header.php) | [evidence](evidence/browser-tests.json) | 4198842 |
| R15 | Validated dynamic user inputs and native PDO binding | **PASS** | [team05/includes/queries.php](../team05/includes/queries.php) | [evidence](evidence/prepared-queries.json) | 3dcb986 |
| R16 | Date/number/check/select/buttons | **PASS** | [team05/includes/view.php](../team05/includes/view.php) | [evidence](evidence/browser-tests.json) | 4198842 |
| R17 | PHP Session retains conditions across pages | **PASS** | [team05/includes/session.php](../team05/includes/session.php) | [evidence](evidence/common-http.json) | 4198842 |
| R18 | Successful COMMIT and actual intermediate-failure ROLLBACK | **PASS** | [team05/includes/plans.php](../team05/includes/plans.php) | [evidence](evidence/plans-tests.json) | fba9c9f |
| R19 | Central config and checked local override | **PASS** | [team05/config.php](../team05/config.php) | [evidence](evidence/clean-install.json) | e660795 |
| R20 | team05 DB/user/password; no root app connection | **PASS** | [team05/config.php](../team05/config.php) | [evidence](evidence/schema.json) | e660795 |
| R21 | Install exactly under htdocs/team05 (actual Linux XAMPP; professor Windows host NOT_RUN) | **PASS** | [team05/index.php](../team05/index.php) | [evidence](evidence/xampp-install.json) | 4198842 |
| R22 | Fresh XAMPP from PHP+SQL with no API/CDN (actual Linux XAMPP; professor Windows host NOT_RUN) | **PASS** | [tools/verify_xampp.py](../tools/verify_xampp.py) | [evidence](evidence/xampp-install.json) | pending document milestone |
| R23 | Demo source and packaged commit match | **TODO** | [tools/package_release.py](../tools/package_release.py) | [evidence](evidence/release-verification.json) | pending document milestone |
| R24 | At least five base tables; actual six | **PASS** | [sql/dbcreate.sql](../sql/dbcreate.sql) | [evidence](evidence/schema.json) | e660795 |
| R25 | At least five user screens; actual nine | **PASS** | [team05/includes/header.php](../team05/includes/header.php) | [evidence](evidence/browser-tests.json) | 4198842 |
| R26 | Implementation report final rendered minimum 10 pages | **TODO** | [docs/report.md](report.md) | [evidence](evidence/document-render.json) | pending document milestone |
| R27 | English paper final rendered minimum 4 pages | **TODO** | [docs/paper.md](paper.md) | [evidence](evidence/document-render.json) | pending document milestone |
| R28 | ERD/PHP structure/code/schedule/contributions (draft report records all sections; actual human contribution information remains pending) | **PASS** | [docs/report.md](report.md) | [evidence](report.md) | pending document milestone |
| R29 | English PPT, oral presentation and backup video (English draft/script prepared in P9; final oral presentation and submitted backup video NOT_RUN) | **TODO** | [docs/demo-script.md](demo-script.md) | [evidence](demo-script.md) | pending document milestone |
| R30 | Actual individual contributions and author comments (Codex implementation is recorded honestly; team members must supply their actual roles/effort) | **BLOCKED** | [docs/contributions.md](contributions.md) | [evidence](contributions.md) | pending document milestone |

Scope note: NASA retrieval was performed here; KASI/RDA values came from the user-provided verified appendix snapshots. No new final almanac cross-check or RDA full-page download is claimed.

Commits use the existing configured Git identity. They record the Codex-assisted process and do not establish personal human authorship. GitHub HTTPS push is blocked by absent credentials; see progress.md and evidence/git-status.json.
