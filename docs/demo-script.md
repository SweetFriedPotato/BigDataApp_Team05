# English demonstration draft

**Team 05 · Based on executed results · 2026-11-11 (Asia/Seoul)**

This is a rehearsal script, not a claim that the final English presentation or course video has been delivered. Use the review package's COMMIT_SHA.txt to identify the exact code. Keep the same package and source version for the demonstration. Personal speaking parts are not assigned; the team must decide who actually presents and record that contribution.

## Opening

“Seasonal Living Guide compares historical temperature records for five requested locations in Korea. Our period is January 2023 through December 2025. We use NASA POWER gridded reanalysis and Local Solar Time dates. These values describe the past. They are not forecasts or station observations.”

Open Home and point to 5,480 daily records and the four separate analysis menus. Explain that calendar dates and monthly ingredient guidance are separate references. No API or CDN is needed after installation.

## 1. Complex grouping — Temperature Comparison

Open Temperature Comparison. Select all five locations, dates 2024-08-01 to 2024-08-31, daily maximum 28 and daily range 10. Choose location/year/month and Apply filters.

“We count all valid days in the selected dates. A valid day contains mean, maximum and minimum temperature. Both limits must hold for a matching day. These thresholds classify days; they do not remove the nonmatching days before calculating a rate.”

Show the means, period extremes,31 valid days, matching counts and exceedance counts. Change a threshold and show that valid-day counts remain 31 while matches change. Restore 28/10. Change the grouping option to location/year and point out that an annual row represents only the selected dates.

## 2. OLAP — Temperature Explorer

Follow the Explorer navigation link; the common period persists through PHP Session. Choose year view, open 2024, then open month 8. Point to the daily records. Use the exploration path to return to month and year.

“The queries change from year groups to month groups to daily records. Drill choices intersect the comparison dates. The roll-up table computes monthly, annual, location and all-location totals from daily data. Across five locations, a date contributes five location-days.”

Show Annual subtotal, Location subtotal and All selected locations. For a separate correctness example, January–February 2024 has 60 days per location and 300 location-days overall. The mean is daily weighted, not an unweighted average of monthly averages.

## 3. Dense ranking — Find My Season

Restore August 2024, all five locations,28/10, minimum valid days 1. Choose Top 5 then Top 1.

“Our matching rate is matching days divided by valid days. Busan and Daegu both have 2 out of 31, so they share rank 1 at 6.45 percent. Jeju has 1 out of 31 and rank 2. Seoul and Gwangju share rank 3 at zero. Top 1 includes both first-place ties.”

Explain that DENSE_RANK orders full-precision rates and that location ID only makes final display order stable. Show the denominators and minimum-valid-days control. A display-rounding fixture 1/1095 versus 1/1096 is documented in ranking-tests.json; do not replace live results with constants.

## 4. Continuous windows — Temperature Trends

Select Seoul only and display 2024-01-01 through 2024-01-03, metric mean. Apply and switch the focus from 7 to 30 days.

“For January 1, the 7-day average is 1.14 degrees and the 30-day average is 0.30 degrees. These require December 2023 history. The internal query scans 29 days earlier before trimming the display. Windows partition by location and continue across months and years.”

Show the valid frame counts. Then display 2023-01-01 to 2023-01-07 to explain Insufficient history for early frames. Mention that temperature limits never remove days from the window. Restore a useful comparison period before saving a plan.

## 5. Web CRUD and applying a plan

Choose Save these conditions. Enter a clear demonstration title and memo; select two regions and save. Open the persisted details and edit the title, limits or locations. Save unchanged once if useful, demonstrating that a same-value update is accepted.

“Plan creation and modification commit the parent and all selected location links together. The saved plan contains common dates, regions and limits. It does not claim to save grouping or moving-average focus.”

Apply the plan to Ranking, then follow Temperature Comparison and show the same common inputs. Return to Saved Plans, open the plan and delete it. Show that the parent/detail is gone. State that this is a shared demonstration area with no per-person private ownership.

## 6. Actual transaction failure evidence

Open docs/evidence/plans-tests.json or the corresponding report section. Show T 24 and T 25.

“In the create test, the parent insert and first child insert succeed before another child violates the location foreign key. Rollback leaves zero parent and child rows. In the update test, body changes and deletion of old links occur before the failing new child. The original body and region set are exactly restored.”

These are real DB failures tested from CLI, not form rejection presented as rollback. No failure-injection switch exists on the web. If a live rerun is appropriate, use the disposable installation command rather than resetting a real shared database:

```bash
python 3 tools/verify_install.py
```

## 7. Seasonal Information

Select 2024/October and show 한로, 상강 and 새송이버섯 with source links. Compare February 2024 and 2025 to show year-dependent solar-term dates:2024-02-04 versus 2025-02-03 for the first February occurrence.

“Solar terms are KASI calendar reference dates. Food entries are historical RDA monthly editorial selections. They are independent of the location temperatures. Adding a monthly item does not multiply weather counts, because the application uses separate SELECT statements.”

Do not call the calendar snapshot a final-almanac cross-check or imply that a monthly editorial feature proves a harvest date for a selected location/year.

## 8. Installation, offline behavior and version

Show the four SQL files and docs/install.md. Point to xampp-install.json: PHP 8.2.12, Apache 2.4.58 and MariaDB 10.4.32, actual htdocs/team05, team05 account and network mode none. Show create/insert, reset and dump-only restoration PASS with equal data/key fingerprints.

“The required runtime is PHP, Apache and MariaDB. We install the provided SQL before browsing. The actual XAMPP test used no network. Python and Node are developer tools only. The review package identifies its source commit, so the demonstrated code can be matched to the delivered files.”

Close by stating the verification limits: no performance or user study, untested professor physical host, and pending actual human contribution statements. Do not claim the final course upload or live presentation has already occurred.

## Evidence and recovery checklist

- Start the prepared local environment with `./tools/dev.sh up`. Run init only on a new empty project database. The existing prepared database is already initialized.
- Local development URL: `http://127.0.0.1:8055/team05/`. XAMPP default URL: `http://localhost/team05/`.
- Keep `docs/rendered/slides-draft.pptx`, report/paper PDFs, actual result captures and the silent demo preview available as draft aids.
- The silent preview is an actual browser recording without spoken English narration; it is not the final submitted backup video.
- Use retained JSON/screenshots when a live host fails. Describe them as recorded evidence, not a newly executed test.
- Before final submission, have humans confirm personal contributions, review the draft language, rehearse English, check the assigned presentation date and verify the real course upload status.
