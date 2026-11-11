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
