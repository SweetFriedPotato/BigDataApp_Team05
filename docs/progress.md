# Sequential implementation progress

All timestamps use Asia/Seoul. One Codex session; no parallel developers. Source specification is preserved only at `.local/README.spec.md` and is excluded from Git as requested. The delivered README will describe actual results.

## P0 — inspection (2026-11-11)

- Read all 1,157 lines of the original README, including appendices A–D.
- Applicable AGENTS.md: none in `/`, `/home`, user home or BigData; no nested files existed.
- Existing files: README.md only (79,061 bytes); no local Git repository.
- `git ls-remote https://github.com/SweetFriedPotato/BigDataApp_Team05.git`: exit 0, no refs. Existing Git identity: SweetFriedPotato / jiheechoi0102@ewha.ac.kr. No identity was invented.
- PHP, Apache and MariaDB absent from PATH and checked common Linux/XAMPP paths. Docker 29.6.2 daemon is accessible.
- Standard sandbox failed before command execution (`bwrap: loopback: Failed RTM_NEWADDR`); approved elevated execution is used for project commands.
- Next: project-owned Docker containers for Apache/PHP and MariaDB, without changing host packages or existing containers/databases.
- Verification: read-only environment commands, Docker version, Git remote refs. P0 inspection PASS; runtime not yet installed.
- Validated commit: this initial commit (see `git log -- docs/progress.md`). Push result recorded in evidence and next entry.

## P1 — schema and input contracts

- Added the six exact schema tables, keys, CHECKs and date index; administrator operations are excluded from required SQL.
- Added central evaluation defaults and validated local override, strict common filters and per-page option whitelists.
- Added isolated Docker runtime definition with an internal network and a localhost-only web port. Existing host services are untouched.
- P0 push failed: `could not read Username ... terminal prompts disabled`. Local commit bfec3f7 exists; authentication remains unavailable.
- Verification before this commit: `docker compose config --quiet`, `git diff --check`; PHP runtime and schema execution pending P3/P4. The commit is a contract/setup milestone, not a claim of runtime PASS.

## P2 — acquired and validated data

- Downloaded five actual NASA CSVs sequentially; 5,480 rows, zero date/missing/order defects, 2024 leap day present for all locations.
- Preserved collection timestamps and hashes; used supplied KASI/RDA appendix snapshots with their provenance explicitly distinguished from new downloads.
- Created deterministic normalized CSVs and plain INSERT seed; repeated generation produced the same SHA-256.
- Independent raw-CSV Decimal oracle confirms the August 2024 tied ranking and Seoul 2024-01-01 windows.
- Commands: `python3 tools/build_seed.py` (twice), `python3 tests/oracle.py`, `python3 -m py_compile tools/*.py`, `git diff --check`. Evidence: docs/evidence/data-validation.json, oracle.json, oracle-summary.json; details in data-validation.md.
- P1 push failed for the same missing HTTPS credentials. All implementation continues locally. P2 tests T01–T03 PASS; database calculations not yet claimed.

## P3 — real schema execution

- Started project-owned Apache/PHP and MariaDB containers; imported `dbcreate.sql` then `dbinsert.sql` as team05.
- `docker compose exec -T web php /workspace/tests/schema.php`: PASS; six InnoDB tables, exact 5,569 seed rows, correct PK/FK/index metadata. Invalid FK/duplicate PK/CHECK probes rejected; all probes rolled back.
- `php -l` for all P1 files: PASS. PHP 8.2.35 native PDO and MariaDB 10.4.34 verified with ONLY_FULL_GROUP_BY.
- Evidence: docs/evidence/schema.json, php-cli.txt, apache.txt, php-lint-p3.txt.
- Initial HTTP connection failed because Docker's internal-only network suppressed the host mapping. A separate localhost access bridge is being added; HTTP is not marked PASS at this point.
- P2 push failed for missing HTTPS credentials; c9ff724 remains local. P3 validated commit is the commit adding schema evidence; see history.

## P4 — common PHP and nine page routes

- Implemented bootstrap, native PDO, Session, strict filter/option validation, CSRF, escaped view helpers and shared navigation for the four distinct analysis menus.
- Added original responsive English UI using local CSS/JS; Home counts come from MariaDB. Nine routes execute under Apache. Feature skeletons are explicitly marked pending and will be replaced in P5–P7.
- HTTP host mapping now works at http://127.0.0.1:8055/team05/. CLI and Apache both run PHP 8.2.35 with pdo_mysql. Temporary SAPI probe was removed immediately after collection.
- `php -l` all PHP: PASS. Nine routes HTTP 200; `python3 tests/common_http.py`: PASS for cross-page Session, 13 invalid input cases, unchanged Session on invalid submission, CSRF reset protection, HttpOnly/SameSite and denied direct config/includes access.
- Initial HTTP harness encoded its array-date case as a scalar; the assertion correctly failed. Fixed the request key to `start_date[]` and reran the entire check.
- Evidence: php-lint-p4.txt, php-apache.json, common-http.json. P3 push failed for the same credentials issue. Validated P4 commit is the commit adding these files.

## P5a — complex grouping

- Added shared valid/matching/exceedance flags CTE and native prepared complex grouping by location×year×month or location×year.
- Includes all required means, daily-range average, period extremes, exceedance/matching counts and denominator-safe rates. Thresholds never prefilter candidate weather rows.
- `docker compose exec -T web php /workspace/tests/aggregate.php`: T05–T08 PASS against independent raw-CSV Decimal expectations and transactional boundary/null fixtures.
- `python3 tests/common_http.py`: still PASS; real aggregate page HTTP 200. Evidence: aggregate-tests.json.
- P4 push failed for missing credentials. P5a validated commit: commit adding aggregate-tests.json.

## P5b — OLAP and roll-up

- Replaced OLAP skeleton with SQL year/month/day queries, visible drill links and upward navigation. Drill bounds intersect common filters, including an explicit empty intersection state.
- Added real MariaDB `WITH ROLLUP`, outer ordering, annual/location/grand labels and location-day units. All means derive from raw daily records.
- CLI T09–T10 PASS under ONLY_FULL_GROUP_BY. Five years groups / ten month groups / 155 January location-days; partial January has 17 days; grand subtotal is 300 location-days for Jan–Feb 2024.
- Actual Apache HTTP year→month→day→month→year: PASS. Evidence: olap-tests.json. P5a push failed for missing credentials.

## P5c — dense ranking

- Added DB counts→high-precision rates→DENSE_RANK→outer Top N ranks, with integer binding and no tie breaker in the window ordering.
- CLI T11–T13 PASS: 2/4 and 3/6 share rank 1; zero-valid excluded; equal display percentages with different full rates retain different ranks; Top1 includes ties; minimum-valid-days applied before ranking.
- Actual NASA August 2024 matches the independent oracle: Busan/Daegu 2/31 rank1, Jeju 1/31 rank2, Seoul/Gwangju 0/31 rank3.
- Apache Top1 HTTP returns both Busan and Daegu, 6.45% each. Evidence: ranking-tests.json. P5b push failed for missing credentials.

## P5d — continuous windows

- Added DB 7/30-day windows partitioned by location, 29-day lookback before display filtering, complete-valid-day counts, date-span checks and all four metric whitelists. Both frame results are shown; the selected frame is emphasized.
- CLI T14–T18 PASS for 1..35 sequence, display invariance, all 40 raw-CSV cross-year/leap-month oracle cases, insufficient history, missing date and NULL day, location partitions and threshold invariance.
- Actual Seoul 2024-01-01 means: 7-day 1.141429, 30-day 0.301333; Apache displays 1.14/0.30. All eight metric/focus combinations execute via HTTP.
- Evidence: window-tests.json. Synthetic rows exist only inside rolled-back transactions. P5c push failed for missing credentials.

## P6 — transactional saved plans

- Implemented DB-backed plan list/detail/create/edit/delete, shared-space disclosure, Unicode character limits, common-condition persistence and validated apply-to-Session. All mutations use POST+CSRF and PRG; GET actions return 405.
- CLI T21–T25 PASS: committed body/child writes, identical update, location replacement, cascading delete preserving another plan, successful parent INSERT followed by actual child FK failure and zero residues, update/delete-child/failed-insert rollback restoring an exact original snapshot.
- Failure cases call the internal repository boundary only from CLI; no failure switches or test routes exist in the web application.
- `python3 tests/plans_http.py`: actual HTTP CRUD and T26–T27 PASS, including Session reuse, escaped HTML, CSRF403, invalid target422, deleted detail404 and Unicode limits. All test plans cleaned up.
- PHP syntax PASS. Evidence: plans-tests.json, plans-http.json, php-lint-p6.txt. P5d push failed for missing credentials.

## P7 — seasonal references

- Completed year/month selection, independently prepared date-range KASI SELECT and month-bound RDA SELECT, Korean names, direct source links and accurate reference/editorial provenance.
- T03/T28 CLI PASS: 24 terms each year, every month has an item, year-varying February dates, and added food items leave aggregate/ranking/window results exactly unchanged.
- Actual Apache: all 36 year-month selections HTTP200 with source links; four invalid option cases HTTP422. Evidence: seasonal-tests.json.
- P6 push failed for missing credentials. All nine required user screens now have completed behavior; plan_actions is an additional POST handler.
