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

## P8 — integration evidence (ongoing actual XAMPP check)

- Generated sql/dbdump.sql with actual MariaDB 10.4.34 mysqldump; saved plans are empty. Captured row hashes, columns, constraints and indexes plus representative bound analysis SQL.
- Fresh uniquely named MariaDB/PHP Apache environment PASS: create→insert→all9screens, full calculation/transaction suite, drop→create→insert, zero-table dump-only restoration, exact semantic fingerprint, internal-network-only execution, blocked public request and changed copied path/local config host. Primary runtime was preserved.
- Actual Chromium 141 PASS: desktop 1440×1050, mobile 390×844 across eight routes, dynamic filters, tied ranks, drilldown/up, 7/30 focus, seasonal date, plan CRUD/apply and escaped memo. Zero console errors. Four screenshots are genuine browser captures.
- Visual inspection found missing Korean glyphs on the Linux browser; bundled Nanum Gothic under OFL and reran browser checks/captures successfully. No CDN/font download is needed at runtime.
- Fixed an integration inconsistency: created/updated timestamps were labeled KST while MariaDB used its default time zone. PDO now sets the connection time zone to +09:00; no global server setting changed.
- Final PHP syntax check PASS; T01–T33 currently PASS. T34 packaging NOT_RUN. `tools/record_results.py` generated the matrix from actual evidence only.
- Official XAMPP Linux 8.2.12 installer downloaded from the project's SourceForge mirror, hash recorded; installation inside a new Ubuntu container is still running. XAMPP-specific requirements remain TODO until actual execution finishes.
- P7 push failed for missing HTTPS credentials. Remaining work: finish the XAMPP check, commit integration evidence, then P9 documents and a concrete demo package.

## P8 — official XAMPP compatibility completed

- Official installer completed with exit code 0. Slow progress was actual manual-page symbolic-link creation, not a runtime test PASS. Two opaque Docker-build attempts were interrupted; a project-owned no-network install container made file/log progress observable. The installed image was saved only after stopping its services.
- Fresh actual XAMPP `/opt/lampp/htdocs/team05`, unmodified public config, team05@localhost: PASS. Docker `--network none`; no API/CDN possible.
- All six calculation/transaction suites and HTTP across nine screens/CRUD/Session PASS; drop→create→insert PASS; dump-only import with the actual bundled XAMPP mysql client PASS; semantic fingerprints match the original MariaDB seed/dump; local config override PASS.
- Explicit Apache-vs-CLI SAPI/version/extension probe was added and the fresh run repeated for that unresolved environment check: PASS. Temporary probe removed.
- Evidence: xampp-install.json and xampp-installer-log.txt. `tools/verify_xampp.py` reproduces verification with an existing image; prepare_xampp.sh installs the official package in isolation. Windows/macOS/professor physical host remain NOT_RUN.
- Adversarial real HTTP test PASS: SQL metacharacter title remains text, script memo escaped, duplicate IDs normalized, malformed action/id/array CSRF rejected; no table loss. Runtime PHP warning/fatal/parse/notice count is 0. Five NASA hashes exactly equal supplied references.
- P8a push failed for missing credentials. P0–P8 runtime implementation/verification complete; T34 package identity will be checked after the P9 document freeze.

## P9 — evidence-based documentation and demo drafts

- Completed report.md (15 substantive chapters), paper.md (English academic draft), actual six-table ERD/PHP flow Mermaid sources and original SVGs, contributions.md with unconfirmed human activities explicitly pending.
- Rendered report/paper with Chromium; actual counts are 18 and 7 pages. All figures loaded; PDF text extraction finds no blank pages. Representative actual PDF pages visually inspected. A text-formatting pass had split utf8mb4/team05 in the paper; corrected the identifiers, regenerated PDFs and checked their extracted text.
- Captured two actual result-table figures for the paper (within the specified 1–4 figure range). Four full UI screenshots remain as browser evidence.
- Created English demo-script.md, slides.md and a 12-slide PPTX draft. PPTX reopened successfully with python-pptx; actual PowerPoint render/rehearsal NOT_RUN. Recorded a real silent Chromium demo of analyses, OLAP, plan create/edit/apply/delete and seasonal information; all rehearsal test plans deleted. Silent preview is not a claimed final English oral/video submission.
- Replaced README.md with an implementation/installation entry point after byte-checking the preserved original at .local/README.spec.md. Original remains ignored and is not part of Git/ZIP.
- Added exact-commit review packaging tool and pinned optional developer document/browser dependencies. Runtime still needs only PHP/Apache/MariaDB and supplied SQL.
- `record_results.py` and `record_requirements.py` link actual evidence. R26/R27 satisfy rendered draft minimums; final human review remains pending. R29 final presentation/video and R30 actual individual contributions are not fabricated as complete.
- P8b push failed for missing HTTPS credentials. Local commits continue. Next: verify links and source cleanliness, commit documentation, run exact-commit package verification and freeze a review tag.

## Review package verification and final workspace state

- First actual review ZIP from committed P9 source 7159ab4 PASS: 149 committed payload members byte-identical to Git; current team05/ and sql/ bytes match that same source. Identity and SHA-256 are in the generated ZIP metadata and dist/review-verification.json.
- T34 now PASS; all T01–T34 have executed evidence. The final package is regenerated from this evidence-freeze commit; COMMIT_SHA.txt / RELEASE_MANIFEST.json / VERIFICATION.json are authoritative for the current review artifact and avoid self-referential hashes inside tracked source.
- Final main DB fingerprint after all browser/recording work equals the baseline: zero surviving rehearsal plans or synthetic records. Demo WebM codec, resolution and duration were checked with the bundled ffmpeg.
- Local Markdown link audit PASS, including generated document/media files. Original 79,061-byte specification remains local and ignored; no private config/token is in the staged payload.
- Stopped only the owned Compose runtime during teardown; named DB volume seasonal-team05_seasonal_db is preserved. Restart with `./tools/dev.sh up`; do not reinitialize the existing prepared DB. XAMPP test/diagnostic containers were removed.
- P9 push again failed for absent GitHub HTTPS credentials. Local commits and a review tag preserve the result; no force push or remote history rewrite. The current local commit/tag and final ZIP SHA are reported by the packaging/final Git commands, not fabricated in this document.
- P0–P8 implementation and actual runtime verification completed. P9 report/paper/slides/script/recording drafts completed. Report18/paper7 rendered pages. R29 final oral presentation/submitted video and R30 actual individual human contribution statements remain TODO/BLOCKED; Windows/macOS/professor physical host and actual course upload NOT_RUN.

## Revision A — inspected and preserved baseline (2026-11-12, Asia/Seoul)

Read all 585 lines of the local revision instruction. No applicable AGENTS.md exists in the project/ancestors. The working tree was clean. Local HEAD, origin/main and the dereferenced review-2026-11-11 tag were verified against GitHub at 7c7c8509266f38d02f49965ee89f2bef0d53619a. GitHub authentication is now working; earlier push failures above remain historical events.

Started the existing Compose runtime without init/reset. Backed up the prepared DB privately to .local/revision/backups/pre-revision.sql and recorded its complete row/key/column fingerprint. Original data, SQL and query source hashes are in evidence/revision-2026-11-12/baseline.json. Before-UI captures are preserved in that evidence directory. The initial capture command loaded Playwright before setting its binary path; it failed without producing images. Corrected the environment order and captured all three baseline pages successfully. All destructive/failure/CRUD tests in this revision use new disposable databases and will not delete existing Saved Plans.

The new responsibility assignment supersedes the earlier no-assignment condition: each member has 20% technical, document and presentation responsibility. Actual human review/work completion remains separately recorded. One Codex session continues sequential implementation; no additional developers or history rewriting.

## Revision B1 — evidence aggregators

Reproduced the old generator's 34-PASS false-positive behavior only in a temporary fixture copy of commit 7c7c850. Replaced hardcoded status defaults with field-level evidence checks and explicit PASS/FAIL/PARTIAL/NOT_RUN/BLOCKED states. Date sets, missing/order counts, schema counts/keys and required execution provenance are checked independently. Executed file hashes distinguish current worktree evidence from old runs; matrix-generation timestamps never masquerade as execution dates. Requirement judgments combine mapped tests and complete document/human scope; file presence cannot make R28 PASS.

`python3 tests/evidence_regression.py` verified normal, failing, missing and incomplete fixtures, actual count display, requirement propagation and nonzero strict-mode exits. Evidence: evidence/revision-2026-11-12/evidence-regression.json. Real historical evidence files were not overwritten. The production matrices will be regenerated after fresh revision runs; missing future UI/document evidence is intentionally not declared PASS.

## Revision B2 — plan fixes, UTF-8 and accurate runtime descriptions

Reproduced T35–T38 failures in the disposable revision lab before changing product code: region-only updated_at stayed old; memo0 showed No memo; un-applied current inputs were not forwarded; an unknown save intent was silently accepted. Added explicit CURRENT_TIMESTAMP to the parent UPDATE in its existing transaction, restricted filter intents with a validated save→plan-form redirect, and changed memo fallback to null/empty only. Same-value saves remain valid. T35–T38 now PASS; FK failure restores the exact body/regions/timestamp snapshot.

Removed PHP8.1-only never from the handler (void plus exit), fixed python3 command text, and distinguished PHP8.0 syntax target from actually tested PHP8.2 runtimes. Data text I/O explicitly uses UTF-8 with CSV newline handling retained. A guarded real seed rebuild verified all original data and seed bytes unchanged. No NASA re-download or main DB reset occurred.

HTTP helpers now report actual base URL/server/client environment and explicitly leave network isolation to the outer verifier. Existing common HTTP/Session tests, original CRUD/rollback suite, new regressions and PHP syntax checks passed on the disposable lab. Evidence is under evidence/revision-2026-11-12; the original historical JSON/logs are preserved. Current GitHub refs are observed by tools/git_status.py rather than an authentication-failure constant.

## Revision C — compact original weather UI

Added an original sun/cloud SVG shared by header/footer/favicon, a compact 7-menu header and clean sans-serif blue/white design tokens. Removed decorative star/rings/badge and oversized headings. Home uses real DB counts and a 2×2 analysis layout. Common filters retain native inputs, visible checkbox selections, current-input Save conditions and reset. Server validation now associates errors with the relevant input and preserves safe draft values without updating Session.

Comparison presents the seven main columns first; all original remaining measures remain in More statistics. Definitions/source details move below results. No analysis SQL, data value or schema was changed. Actual browser captures at 1440×900/1366×768/390×844/360×844 have no page overflow. The first comparison row starts at y≈691 on both desktop sizes. Home/comparison screenshots were visually inspected; six text/background pairs exceed 4.5:1. Original aggregate and common-Session regressions still pass on the disposable lab. Full nine-screen and graph checks follow in D/G.

## Revision D — nine screens and SQL-derived trend graph

Applied the compact style consistently across comparison, OLAP, ranking, trends, seasonal and all plan screens. Kept all four analysis URLs, all existing statistics and ROLLUP labels. Added one-location daily/MA7/MA30 SVG plots using the returned SQL values only. Distinct line styles, focused 7/30 selection, real date spacing, gaps/NULL breaks and a finite single-day point are implemented. Mobile SVG coordinates use the same values with a narrower viewBox; graph selection never changes global comparison locations.

T41 verifies geometry and actual SVG XML rendering against SQL values. Full Chromium regression passed all nine valid user screens plus edit at 1440×900, 1366×768, 390×844 and 360×844; includes all5480 rows, Top1 ties, hierarchy up/down, empty results, Unicode long title/memo, memo0, real create/edit/apply/delete confirmation, keyboard/error association and Save conditions without JavaScript. No unexpected console/external runtime requests or document overflow. During validation, missing explicit column scopes and an extracted SVG helper variable were caught, corrected and covered by the assertions; they are not left as false PASSs.

PPT renderer setup succeeded after isolating the actual DNS failure and using a verified Ubuntu mirror address only for the build. No host resolver or package configuration was changed. Actual slide rendering is still pending F/H. Matrices now reflect the new evidence directory: tests not rerun for this source and not-yet-generated release/document evidence are PARTIAL/NOT_RUN, rather than inheriting historical PASSs.

## Revision E — equal responsibility assignment

Created the confirmed five-member technical/report/paper/presentation table with 20% each and two content slides each (2–3, 4–5, 6–7, 8–9, 10–11; title/reference slides shared). Common integration/English editing/video/final checks are equally assigned. Added Team responsibility comments to the related PHP/SQL files and function-specific owners to shared queries. Comments identify responsibility, retain Codex implementation history and do not fabricate a person's coding or review completion.

Updated contributions.md with both the assignment and a separate actual-confirmation table. All actual human reviews, oral presentation and course upload remain NOT_RUN in human-review.json. The responsibility checker initially caught the HTML-only footer missing its comment; corrected it and ensured all five assignment rows are present. Assignment/code-label consistency and guarded UTF-8 regeneration now pass. Baseline comparison confirms every data file/hash unchanged and every SQL script body/core query code unchanged after ignoring the intentional responsibility comments. The original DB was not reset.

## Revision F–G — reproducible source documentation and full execution (2026-11-12 KST)

- Deployed application commit e12ee89cd59964d2e58e601a7acfcd537dcecce8 from a Git ZIP into a separate read-only Apache document root at http://127.0.0.1:8057/team05/. Actual container file hashes and HTTP asset bytes match manifest d47b9d5e12cc2858180e0d2937908453c683417a0613ce4c73b5578d3f86a525. Primary prepared DB remains separate.
- `python3 tools/run_checks.py`: schema, all original SQL suites, real plan FK rollbacks, timestamp/order regression, chart geometry and common/plans/adversarial/revision HTTP checks passed. Disposable DB fingerprint was identical afterward. Metadata identifies real commands/environment/tested files. Old evidence paths are preserved.
- `python3 tools/validate_data.py`, `python3 tests/oracle.py`, `python3 tests/evidence_regression.py`, `python3 tests/utf8_regression.py`: passed; raw data/seed values remain unchanged. Evidence-generator fixtures include normal, failing and missing classes, strict nonzero exits and the historical false-PASS reproduction.
- `python3 tools/verify_install.py`: T29–T33 passed including actual internal-network inspection and blocked public egress. `python3 tools/verify_xampp.py`: actual official Linux XAMPP PHP8.2.12/Apache2.4.58/MariaDB10.4.32 passed create/insert, all screens/CRUD, all original and new CLI suites, DROP/recreate, dump-only restoration, config override and network=none. Primary DB was not reset.
- `SLG_BASE_URL=http://127.0.0.1:8057/team05/ SLG_CAPTURE_DIR=docs/evidence/revision-2026-11-12/screenshots/after node tests/browser.mjs`: all nine screens plus valid edit at four viewports, keyboard, no-JS saving, long Korean strings, full5480 rows, empty/error states passed; no unexpected console errors/external runtime requests/page overflow. Nine desktop and nine mobile captures retained with source/URL/time/hashes.
- Report/paper updated to confirmed equal 20% responsibilities and actual automatic module results. Seventeen exact source listings generated with file/line/hash references by `tools/update_report.py`; Session start, native PDO, CRUD/rollback, controls and four analyses included. Actual human sign-off remains NOT_RUN.
- `node tools/capture_figures.mjs`: initial capture selector did not exist and timed out; corrected tool to actual `.trend-panel`, reran successfully (7 figures). No app change was needed. PDF generation passed actual page checks: report24, paper8. PPT generation completed; actual rendering/visual review is a separate subsequent check.
- Current matrix after these executions: 41 PASS, 3 NOT_RUN (T34 packaging, T42 media identity, T44 complete artifact review). These pending checks are not described as passed.

## Revision H — same-application media and rendered submission drafts (2026-11-12 KST)

- Final application captures: 9 desktop +9 mobile screenshots;7 report/paper figures. Actual source/URL/container/recording times and SHA-256 manifests retained in browser-tests.json, figure-capture.json, served-app.json and deployment-media.json. Final committed-source application identity remains e12ee89 / d47b9d5e12cc…; no PHP/SQL/asset changes after freezing it.
- `node tools/render_documents.mjs`: report24 actual PDF pages, paper8 pages. Visible Figure1/2 captions verified from the English PDF. No automatic chapter page breaks used to pad the report. Seventeen exact code excerpts match current source; source/line/file hashes reproduced by tools/update_report.py.
- `python3 tools/make_slides.py` + `python3 tools/render_slides.py`: all12 PPTX slides actually rendered by LibreOffice7.3.7.2 to PDF and individual PNGs. Text completeness/page bounds checked. Initial small ERD/figure sizing improved. A later geometry check caught overlapping reserved text/image rectangles on8/10/11; text box height corrected, rerender passed with overlaps=[], outside=[], missing_rendered_text=[]. Hash verification rejected the stale earlier render proof; generators now persist failure output. Codex inspected all12 final PNGs individually; actual student sign-off remains NOT_RUN.
- `python3 tools/check_submission.py`: report/paper page counts, visible captions, all required report features,17 source excerpts, five20% shares in all four dimensions, correct two-slide assignments and exact reviewed slide hashes passed.
- `node tools/record_demo.mjs`: actual20-scene English-captioned browser video,248.44sec (4min8.44sec),1440×900,21,431,692bytes, SHA-25642be20b6d5cc2822d22327fd230ec9679e3968957e407e817e1f06f0bd021a4e. Real current-input save, memo0, region-only timestamp, CRUD, Session, SQL modes/chart and seasonal reference flow recorded. T24/T25 shown as recorded real CLI evidence, explicitly not a live web failure switch. No audio/human oral presentation claimed. Initial SVG-document caption overlay failed; wrapper fixed and recording restarted from the beginning. Final decoded frames35/185/245sec inspected for readable captions and actual behavior.
- Prepared primary DB fingerprint rechecked against private pre-revision backup; every row/key/type/index hash identical. Original historical evidence JSON remains byte-identical. PHP lint, UTF-8 generator regression, evidence fixtures and responsibility checks rerun successfully. Technical matrix has43 PASS and T34 packaging NOT_RUN at this stage; actual human review/oral/course upload remain separate.

## Revision I — committed package verification and final handoff (2026-11-12 KST)

- `python3 tools/package_release.py --record-evidence`: package snapshot c8c6cf43dd260c39cc4cf232a613bffc865393d9 verified all271 payload members against Git, every working-tree byte, actual Apache serving-root PHP/CSS/JS/SVG/font/HTTP asset bytes,18 capture hashes and video/application identity. Snapshot ZIP24,210,842bytes, SHA-256b9058b56de9bd81b97f48a1f2c81fec12673f4c58d47fda449455e91be5f1f41; concrete uniquely named snapshot retained in dist. Old package/tag preserved. New alias is dist/team05-review-2026-11-12.zip; final payload commit is COMMIT_SHA.txt inside it.
- `python3 tools/verify_package_install.py --archive dist/team05-review-2026-11-12.zip`: ZIP extracted under /tmp outside Git, no .local or original workspace mounted into XAMPP. The extracted archive's own verifier passed actual fresh official Linux XAMPP create/insert, nine screens/web CRUD, original and revision SQL/transaction/chart suites, DROP/recreate, dump-only restoration, local override and network=none. Inner git identity is absent as expected; tested file hashes identify source.
- `python3 tools/record_results.py --fail-on-error`: all44 actual checks PASS; exit0. `python3 tools/record_requirements.py`:27 PASS and3 PARTIAL (R28/R29/R30 human scope). Strict full requirement generation returned1 as expected despite all technical artifacts being present. Actual member sign-off, oral delivery and course upload are NOT_RUN, not fabricated PASSs. PHP8.0 runtime, Windows/macOS, professor physical host and KASI final-almanac comparison remain unexecuted.
- This commit records the concrete completed snapshot tests. To avoid self-reference, the final clean commit is then repackaged without rewriting tracked evidence; every final payload member and actual serving app is rechecked. Final ZIP installation is repeated from that exact file, with concrete results in dist/final-package-install.json. The annotated review-2026-11-12 tag and remote refs are checked after successful final packaging; final observed SHA/checksum/ref/volume state is recorded in dist/final-status.json. These external final records identify this committed payload without embedding its own commit hash in itself.
- After final checks, only the owned temporary review/lab resources and preview runtime are stopped. Existing seasonal-team05_seasonal_db volume is retained. Restart the prepared application with `./tools/dev.sh up` and open http://127.0.0.1:8055/team05/; do not init/reset that volume. Private original DB backup remains under .local/revision/backups/.
