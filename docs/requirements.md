# Requirements traceability

Current judgments are derived from executed test evidence and complete requirement scope. PARTIAL does not mean a failed SQL calculation; it can identify a pending human review or an artifact not yet verified. The generation time is not a test execution time.

| ID | Requirement | Status | Implementation | Mapped evidence / remaining scope |
|---|---|---|---|---|
| R01 | Weather Data Analysis scope | **PASS** | [team05/index.php](../team05/index.php) | T01, T02;  |
| R02 | Six-table DDL with keys and indexes | **NOT_RUN** | [sql/dbcreate.sql](../sql/dbcreate.sql) | T04;  |
| R03 | Deterministic plain INSERT seed | **PARTIAL** | [sql/dbinsert.sql](../sql/dbinsert.sql) | T01, T02, T03, T40;  |
| R04 | Project-only DROP and reinitialization | **NOT_RUN** | [sql/dbdrop.sql](../sql/dbdrop.sql) | T30;  |
| R05 | Actual DB dump and dump-only restore | **NOT_RUN** | [sql/dbdump.sql](../sql/dbdump.sql) | T31;  |
| R06 | Web INSERT | **NOT_RUN** | [team05/plan_actions.php](../team05/plan_actions.php) | T21, T27;  |
| R07 | Web SELECT/list/detail | **NOT_RUN** | [team05/plan_detail.php](../team05/plan_detail.php) | T21, T27;  |
| R08 | Web UPDATE including selected locations/timestamp | **NOT_RUN** | [team05/includes/plans.php](../team05/includes/plans.php) | T22, T27, T35;  |
| R09 | Web DELETE and cascading children | **NOT_RUN** | [team05/plans.php](../team05/plans.php) | T23, T27;  |
| R10 | Complex grouping and weighted valid-day statistics | **NOT_RUN** | [team05/aggregate.php](../team05/aggregate.php) | T05, T06, T07, T08;  |
| R11 | OLAP hierarchy and WITH ROLLUP | **NOT_RUN** | [team05/olap.php](../team05/olap.php) | T09, T10;  |
| R12 | Dense ranks, ties and Top N ranks | **NOT_RUN** | [team05/ranking.php](../team05/ranking.php) | T11, T12, T13;  |
| R13 | Continuous SQL 7/30-day windows | **PARTIAL** | [team05/window.php](../team05/window.php) | T14, T15, T16, T17, T18, T41;  |
| R14 | Four separate menus and URLs | **PARTIAL** | [team05/includes/header.php](../team05/includes/header.php) | T43;  |
| R15 | Validated dynamic inputs and native prepared statements | **PARTIAL** | [team05/includes/queries.php](../team05/includes/queries.php) | T05, T09, T13, T16, T20;  |
| R16 | Dates, numbers, checkbox, select and buttons | **PARTIAL** | [team05/includes/view.php](../team05/includes/view.php) | T43;  |
| R17 | PHP Session shared comparison conditions | **PARTIAL** | [team05/includes/session.php](../team05/includes/session.php) | T19, T26, T37, T38;  |
| R18 | Real COMMIT and intermediate-failure rollback | **NOT_RUN** | [team05/includes/plans.php](../team05/includes/plans.php) | T21, T24, T25, T35;  |
| R19 | Central configuration with local override | **NOT_RUN** | [team05/config.php](../team05/config.php) | T33;  |
| R20 | team05 DB and non-root evaluation account | **NOT_RUN** | [team05/config.php](../team05/config.php) | T04, T33;  |
| R21 | Actual htdocs/team05 installation | **NOT_RUN** | [tools/verify_xampp.py](../tools/verify_xampp.py) | T33; Actual tested OS only; professor physical host NOT_RUN |
| R22 | Fresh offline installation from supplied PHP/SQL | **NOT_RUN** | [tools/verify_xampp.py](../tools/verify_xampp.py) | T29, T30, T31, T32; Actual tested OS only; professor physical host NOT_RUN |
| R23 | Package, actual serving root and recorded app identity | **NOT_RUN** | [tools/package_release.py](../tools/package_release.py) | T34, T42;  |
| R24 | At least five base tables; actual six | **NOT_RUN** | [sql/dbcreate.sql](../sql/dbcreate.sql) | T04;  |
| R25 | At least five user screens; actual nine | **PARTIAL** | [team05/includes/header.php](../team05/includes/header.php) | T43;  |
| R26 | Rendered report minimum 10 pages (review draft) | **NOT_RUN** | [docs/report.md](report.md) | T44;  |
| R27 | Rendered English paper minimum 4 pages (review draft) | **NOT_RUN** | [docs/paper.md](paper.md) | T44;  |
| R28 | ERD, PHP structure, actual code, schedule and personal work evidence | **NOT_RUN** | [docs/report.md](report.md) | T44; Assigned 20% responsibility is separate from actual human completion; member_reviews=NOT_RUN |
| R29 | English PPT, actual oral presentation and backup video | **NOT_RUN** | [docs/demo-script.md](demo-script.md) | T42, T44; Assigned 20% responsibility is separate from actual human completion; oral_presentation=NOT_RUN |
| R30 | Equal assigned responsibility, name comments and actual member review | **NOT_RUN** | [docs/contributions.md](contributions.md) | T44; Assigned 20% responsibility is separate from actual human completion; member_reviews=NOT_RUN |

Git synchronization: {"status": "SYNCHRONIZED", "checked_at": "2026-11-12T00:25:07.480529+09:00", "local_head": "aa190e9bc4772a2504222e39aa1f7c52e80b72fe", "remote_main": "aa190e9bc4772a2504222e39aa1f7c52e80b72fe", "existing_review_tag": "7c7c8509266f38d02f49965ee89f2bef0d53619a"}. Historical authentication failures are retained in progress.md; current status comes from this observed snapshot.

KASI/RDA use the supplied reference snapshots; no new official-almanac cross-check is claimed. Windows/macOS, professor-host execution, real member sign-off, actual oral presentation and course upload are not inferred from Linux technical tests.
