# Data validation

Executed `python3 tools/fetch_data.py`, `python3 tools/validate_data.py`, `python3 tools/build_seed.py`, and `python3 tests/oracle.py`.

NASA raw downloads are preserved byte for byte with collection UTC timestamps, SHA-256 hashes, requested coordinates and LST definition in `data/manifest.json`. The 5,480 daily rows contain no duplicate, missing or outside dates, missing temperatures or temperature-order violations. Each location has 365/366/365 rows and the leap day. See `evidence/data-validation.json`.

KASI 72 dates and RDA 12 monthly items were transcribed from the supplied specification appendices. They were not newly downloaded or independently reverified here. Their source URLs, RDA publication dates and snapshot hashes are preserved. KASI is calendar reference material; the final official almanac has not been cross-checked. Food entries are historical monthly editorial guides, independent of weather.

`tests/oracle.py` independently parses raw CSVs and calculates Decimal expectations, without calling the application or data preparation parser. `evidence/oracle.json` records the expected grouped statistics, August 2024 ranks and cross-boundary windows against these raw hashes.

Seed contains 5 + 5,480 + 72 + 12 = 5,569 rows. Saved plans and their links start empty. Synthetic test data is never written to seed files.

Seed SHA-256: `5113725dffc2c9de6f9f95f8edb25bde398a4a3a3b99b0e0437d2728e5975513`.

All five newly retrieved NASA SHA-256 hashes exactly match the supplied appendix C hashes. The independently checked August ranking and Seoul cross-year windows therefore use the same source byte versions as the specification.
