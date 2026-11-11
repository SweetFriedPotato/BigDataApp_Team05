# English presentation draft — 12 slides

1. Seasonal Living Guide — historical regional temperatures and seasonal references; Team05; draft and contribution review status.
2. Question and scope — compare the same historical period; five requested points; limits express preferences.
3. Data — NASA5480 rows, KASI72 dates, RDA12 monthly items; LST; source hashes and separate reference provenance.
4. Relational design — six InnoDB tables; composite weather key; plan association FKs; reference tables have no weather FK.
5. Complex grouping — location/year/month, common valid-day denominator, raw-day means and threshold flags.
6. OLAP — year→month→day→up; intersected dates; WITH ROLLUP and location-day subtotals.
7. Dense ranking — August2024 actual table, both tied first-place locations returned by Top1.
8. Windowing — lookback before display; Seoul January1,2024 values1.14/0.30; incomplete frames and location partitions.
9. Plans and Session — actual create/read/update/delete; atomic parent/links; saved common filters applied across pages.
10. Failure and input evidence — real create/update FK rollbacks; literal SQL text, escaped script, CSRF and malformed controls.
11. Reproducible installation — SQL4, fresh official XAMPP, team05 defaults, no network, dump-only restoration/fingerprints.
12. Demo and limits — same-commit review package; no unmeasured performance claim; actual human contributions, final presentation and course upload pending.

Speaker narrative and exact interaction steps are in demo-script.md. No speaking role is assigned automatically. The generated PPTX is a review draft; a human should open and rehearse it in the intended presentation software.
