# Seasonal Living Guide

An implemented **PHP + Apache + MariaDB** application for comparing historical temperatures across Seoul, Busan, Daegu, Gwangju and Jeju. English interface, six InnoDB tables, nine user screens, four independent SQL analysis menus, persistent plans and seasonal references.

## Run locally

For the optional isolated Docker environment:

```bash
./tools/dev.sh up
./tools/dev.sh init
```

Run `init` only for a new empty project database; it refuses an existing schema. The prepared workspace database is already initialized. Open **http://127.0.0.1:8055/team05/**. `./tools/dev.sh down` stops this project and preserves its database volume.

For XAMPP, copy **team05/** into **htdocs/team05/**, import `sql/dbcreate.sql` then `sql/dbinsert.sql`, and open **http://localhost/team05/**. Database, username and password default to **team05**; host 127.0.0.1, port 3306. Local differences belong in the ignored `team05/config.local.php`. Full instructions, safe reset and dump restoration: [docs/install.md](docs/install.md).

The runtime requires Apache, PHP 8.x with pdo_mysql and MariaDB 10.4+ (window functions). It needs no Node, Python, Composer, API keys or external assets after installation. Never import reset/drop scripts into an important shared DB without a backup.

## Implemented behavior

| Menu | Route | Database behavior |
|---|---|---|
| Temperature Comparison | aggregate.php | Location/year/month or location/year grouping, means, extremes, matching/exceedance counts |
| Temperature Explorer | olap.php | Year→month→day and upward links; real WITH ROLLUP subtotals |
| Find My Season | ranking.php | Full-precision DENSE_RANK, minimum valid days, Top N ranks including ties |
| Temperature Trends | window.php | Continuous 7/30-day windows with lookback, four metrics, complete-history checks |
| Seasonal Information | seasonal.php | Independent dated calendar and monthly ingredient SELECTs with source links |
| Saved Plans | plans.php | Web create/read/update/delete, atomic parent/locations, validated apply-to-Session |

Home, plan form and plan details complete the nine screens. All analyses use validated inputs and native PDO prepared statements. PHP Session keeps common comparison conditions across pages. Mutation forms use POST/CSRF and escaped output; successful actions use redirects. Saved Plans is a shared demonstration space with no private ownership feature.

## Data and interpretation

- NASA POWER: **5,480 actual downloaded daily rows**, 2023-01-01–2025-12-31, five requested points, **LST** dates. Original bytes, hashes, collection times and requested coordinates are retained. Zero duplicate/missing dates, missing-temperature rows or temperature-order violations.
- KASI: **72** dated solar-term occurrences, adopted from the supplied reference appendix. Public calendar reference; final official almanac cross-check not performed.
- RDA: **12** monthly ingredient items, adopted from the supplied historical editorial references; exact URLs and publication dates retained. They are independent of weather and local harvest timing.
- Six-table seed: **5,569 total reference/data rows**; saved plans initially empty. No synthetic verification rows are part of seed/dump.

Temperature records are historical gridded reanalysis rather than station observations or forecasts. Matching rate means the share of valid days meeting the user's two limits. It does not measure safety, health benefit or general comfort. [Manifest](data/manifest.json) · [Data checks](docs/data-validation.md).

## Actual verification

Development: PHP 8.2.35 / Apache 2.4.69 / MariaDB 10.4.34. Separate official XAMPP Linux 8.2.12: PHP 8.2.12 / Apache 2.4.58 / MariaDB 10.4.32. CLI and Apache SAPI/extensions checked; SQL uses ONLY_FULL_GROUP_BY. Actual htdocs/team05 installation with unchanged defaults and no container network passed.

Verified complex grouping against independent raw-CSV Decimal expectations; OLAP/rollup; dense ties and unrounded rates; cross-year/leap-month windows; web CRUD/Session; actual create/update FK-failure rollbacks; hostile HTTP inputs; fresh installation, drop/reinstall and **actual dump-only restoration with the bundled XAMPP client**. Chromium desktop/mobile flows passed with zero console errors.

```bash
python3 tools/verify_install.py
python3 tools/verify_xampp.py
```

The first command uses existing project runtime images and creates disposable independent resources. The second requires the optional image prepared by `tools/prepare_xampp.sh`. Neither resets the primary project DB. Developer preparation tools are separate from runtime requirements. See [test results](docs/test-results.md), [requirements](docs/requirements.md), [environment](docs/environment.md) and [progress](docs/progress.md).

## Review drafts and delivery identity

- [Implementation report](docs/report.md) · [PDF](docs/rendered/report-draft.pdf): **18 rendered draft pages**.
- [English paper](docs/paper.md) · [PDF](docs/rendered/paper-draft.pdf): **7 rendered draft pages**, two actual result-table figures.
- [English demo script](docs/demo-script.md), [slide outline](docs/slides.md), [12-slide PPTX draft](docs/rendered/slides-draft.pptx) and [silent actual-browser preview](docs/rendered/demo-preview.webm).
- [Actual contributions / pending human review](docs/contributions.md).

`tools/package_release.py` builds a review ZIP from a clean Git commit, writes COMMIT_SHA.txt and a SHA-256 file manifest, verifies every payload member against Git, and verifies the live demo PHP/SQL bytes against the same commit. It excludes untracked secrets, local configuration, the original local specification and .git. The original supplied README is preserved only at `.local/README.spec.md`; this replacement README describes actual implementation.

The PDFs and slides are drafts. Actual personal contribution statements, English oral presentation, final video/submission review, professor-host verification and course upload remain human work. Windows/macOS were not tested. The original 15 commits and review-2026-11-11 tag have been pushed and verified against GitHub. Current revision synchronization is recorded with observed SHAs in docs/evidence/revision-2026-11-12/git-status.json. No final course-submission tag is implied by a review tag.
