# English demonstration and presentation draft

Team 05 · Revision 2026-11-12 (Asia/Seoul). The application is commit `e12ee89cd59964d2e58e601a7acfcd537dcecce8`; use the final ZIP manifest for the separately identified document/package commit. All demonstration captures come from the committed-source server, not an arbitrary working directory.

Each person has 20% technical, report, English paper and presentation responsibility. Slides 1 and 12 are shared; slides 2–3 belong to Nunnalin, 4–5 to Jieun, 6–7 to Sumin, 8–9 to Koo Daon and 10–11 to Jihee. Integration, English editing, PPT/video and final checks are shared equally. When total duration T is agreed, allow approximately T/5 per person. No official total duration is inferred. The captioned recording is a real browser demonstration, without human speech; actual member review, oral delivery and course upload remain NOT_RUN.

## Shared opening — slide 1

“Seasonal Living Guide compares historical temperature records for five requested points in Korea. Four separate SQL analyses answer different questions. Users can save comparison conditions and apply them across pages. Calendar dates and monthly ingredients are independent reference information.”

Open Home. Show the four analysis menus and 5,480-row total. The local sun/cloud icon and blue/white compact layout are original project assets. No external API, CDN, Node or Python is needed after installing PHP/MariaDB and importing SQL.

## Nunnalin Heimvichit (2371001) — slides 2 and 3 — 20%

“Our period is January 2023 through December 2025, with 1,096 daily records for each of Seoul, Busan, Daegu, Gwangju and Jeju. NASA POWER supplies gridded reanalysis on Local Solar Time dates. These are historical values, not forecasts or urban station measurements. The preserved raw hashes match, and the date checks include leap day.”

Show the actual six-table ERD. Point to the weather composite primary key, date/location index, location foreign key and pairwise temperature CHECK. Point to saved_plans/plan_locations and cascading deletion. Solar terms and monthly food guides have independent date/month lookups and no artificial weather foreign keys.

“Four SQL files support reinstallation: dbcreate defines six tables; dbinsert contains deterministic plain INSERT statements; dbdrop removes only project tables; dbdump is actual MariaDB dump output. In fresh isolated databases we verified initialization, DROP/recreate and dump-only restoration. The actual Linux XAMPP test used htdocs/team05, the team05 account and network mode none.”

Show revision `data-validation.json`, `schema.json`, `clean-install.json` and `xampp-install.json`. Do not run destructive SQL against the existing prepared database. The administrator account is used only to provision a fresh test database; application queries use team05.

## Jieun Hwang / 황지은 (2376329) — slides 4 and 5 — 20%

“Common dates, region checkboxes and decimal limits are validated before Session changes. Unknown options, empty locations and invalid dates return an error while keeping the previous conditions. PDO uses native prepared statements with typed bound parameters. Core forms work without JavaScript.”

On Temperature Comparison, change a date and click **Save conditions before Apply**. The current form reaches Create a Plan; no permanent INSERT happens until Save plan. Return to comparison and demonstrate a field-associated validation message. The compact primary table has seven columns, and More statistics retains every other metric.

“Seasonal Information uses actual year/month dates for terms and month numbers for ingredients. February's first reference is 2024-02-04 in 2024 and 2025-02-03 in 2025. KASI/RDA snapshots were supplied reference material; final official-almanac cross-check was not performed. An extra food item cannot multiply temperature records because the lookups are separate.”

Show February 2025 and the source links. State that monthly editorial ingredients do not prove harvest timing for a selected location/year. The app makes no nutrition, health or safety claim.

## Sumin Cho / 조수민 (2376274) — slides 6 and 7 — 20%

“Plans persist a title, common dates/limits, memo and selected regions. POST and a Session-bound CSRF token protect writes. Names and memos are bound as values and escaped when displayed. Success uses a 303 redirect.”

Create a clearly named temporary plan with memo `0`; show that zero is rendered literally. Edit only region selection and save. Explain that explicit updated_at=CURRENT_TIMESTAMP updates the parent and newest-first list order, including location-only and same-value saves. Apply the plan to Ranking; show that common filters persist to another analysis. Delete the temporary plan and verify its detail is gone. Other records remain intact.

“Each parent and its selected-location links commit together. Our real CLI create test inserts a parent and first child before another child violates an FK. Rollback leaves no partial parent or links. The update failure restores body, selected regions and timestamp exactly. A validation rejection is not our rollback evidence.”

Show T24/T25 in `docs/evidence/revision-2026-11-12/plans-tests.json` and T35 in `revision-functional.json`. There is no public web failure switch. To rerun in a disposable database only:

```bash
python3 tools/verify_install.py
```

The captioned video explicitly labels these JSON results as recorded real CLI evidence, rather than pretending to trigger a failure from a web form.

## Koo Daon / 구다온 (2476009) — slides 8 and 9 — 20%

“Thresholds classify every valid candidate day. They do not remove nonmatching records before calculating denominators. Grouping by location/year/month or location/year changes actual SQL dimensions. Means are weighted by valid daily rows.”

Compare 2024-01-01 through 2024-02-29 for all five points. Each location has 60 valid days. Seoul's partial-year daily mean is 0.018667°C. Show More statistics, including mean maximum/minimum, extreme high/low and matching counts. These are retained original SQL results, not replacement client calculations.

For August 2024, follow Explorer year → 2024 → month 8 → daily records, then the breadcrumb path upward. There are 155 location-day records across five points and 31 dates. Drill intervals intersect the common dates instead of broadening them.

“WITH ROLLUP calculates monthly rows, annual subtotals, location subtotals and a grand total from the original daily observations. Five points over January–February contribute 300 location-days. This is not 300 distinct dates, and the subtotal mean is not an unweighted average of monthly means.”

Open the separate roll-up panel and point to its explicit subtotal labels. A Seoul January 15–31 intersection returns 17 rows.

## Jihee Choi / 최지희 (2276337) — slides 10 and 11 — 20%

Select August 2024, all five locations, maximum 28°C, range 10°C, minimum valid days 1. Show Top 5 and Top 1.

“Busan and Daegu each have 2 matching days out of 31, so both share rank 1 at 6.45%. Jeju has 1/31 and rank 2. Seoul and Gwangju share rank 3 at zero. DENSE_RANK uses full-precision DECIMAL rates, then the display rounds. Top 1 includes both first-place ties.”

Set minimum valid days to 32 to show an explained empty result. The precision fixture 1/1095 versus 1/1096 retains distinct ranks despite equal two-decimal displays. Return to valid conditions.

“Temperature Trends calculates both 7- and 30-day averages in MariaDB. It scans up to 29 days before the display start and partitions only by location. On Seoul January 1, 2024, the results are 1.141429°C and 0.301333°C, displayed as 1.14 and 0.30. December history remains available across the year boundary.”

Show a January graph with Seoul and Busan selected. Change only Graph location to Busan; confirm both remain in the common comparison. Switch 7/30 focus and show the same selected series emphasized in table and graph. Display one day for a finite point, then the beginning of 2023 for Insufficient history. NULL values and missing dates break lines; PHP does not recompute averages. The complete table remains available without JavaScript.

## Shared closing — slide 12

“The original SQL/data/schema remain unchanged apart from responsibility comments. Existing and additional regressions use real raw-data expectations, SQL boundaries, HTTP and all nine responsive screens. Evidence generation rejects missing, failing, incomplete and stale inputs, and strict mode exits nonzero.”

Show `docs/test-results.md` for the actual final test counts, not an outdated copied number. Report/paper page counts come from generated PDFs, and all 12 slides were actually rendered to PDF/PNG and inspected. Images fit both height and width without text overlap.

“The committed-source ZIP, actual Apache document-root hashes, HTTP assets, screenshots and English-captioned video identify one application manifest. The later final package commit is separate and recorded in COMMIT_SHA.txt. The whole ZIP checksum is outside the ZIP. Actual member sign-off, oral presentation, professor-host execution and course upload remain unperformed.”

## Evidence, replay and recovery

- Use `./tools/dev.sh up` to restart the preserved prepared DB at `http://127.0.0.1:8055/team05/`. Do not run init/reset on it.
- Use the packaged `docs/install.md` instructions for a genuinely new XAMPP database. Runtime defaults are database/user/password team05; local configuration can override host/port.
- Keep report/paper PDFs, slides-draft.pptx, its actually rendered PDF and twelve PNGs, result figures and demo-preview.webm together with the package manifest.
- If a live host fails, describe retained evidence as a recording from its stated execution time. Do not call it a newly executed check.
- For a final human submission: each member reviews the assigned module and English content, records actual review notes, rehearses approximately T/5, confirms the course presentation date and performs the real course upload.
