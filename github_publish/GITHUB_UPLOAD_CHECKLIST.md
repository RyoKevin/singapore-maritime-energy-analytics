# GitHub Upload Checklist

This file is for deciding what to publish after the project is cleaned.

## Recommended To Upload

- `README.md`
- `DATA_DICTIONARY.md`
- `requirements.txt`
- `.gitignore`
- `analysis/*.py`
- `dashboard/app.py`
- `docs/index.html`
- `docs/interactive.html`
- `docs/assets/*.svg`
- `analysis/charts/*.svg`
- Key reports:
  - `analysis/output/singapore_maritime_energy_story.md`
  - `analysis/output/twelve_day_vs_2026_comparison.md`
  - `analysis/output/iran_hormuz_exposure_story.md`
- Small processed tables needed by the dashboard:
  - `analysis/output/annual_key_metrics.csv`
  - `analysis/output/bunker_mix_grouped_annual.csv`
  - `analysis/output/iran_hormuz_exposure_annual_shares.csv`
  - `analysis/output/iran_hormuz_exposure_q1_shares.csv`
  - `analysis/output/iran_hormuz_exposure_recent_monthly.csv`
  - `analysis/output/twelve_day_vs_2026_brent_windows.csv`
  - `analysis/output/us_iran_official_q1_impact.csv`

## Consider Uploading

- Official Singapore CSV files under `malacca_strait_data_package/malacca_strait_data_package/data/official_data_gov_sg/`.
- `raw/fred_brent_crude_oil.csv`.
- Other processed CSV outputs if you want full transparency.

## Usually Do Not Upload Directly

- Large FetchSeries Excel workbooks in `raw/` and `data/secondary_fetchseries/`.
- Very large derived long tables if not needed for the dashboard:
  - `analysis/output/oil_imports_long.csv`
  - `analysis/output/iran_hormuz_oil_imports_long_classified.csv`

## Options

- If keeping raw Excel files, use Git LFS.
- If not keeping raw data, include source links and the download script, then document how to reproduce.
- For a recruiter-facing repo, keep the root clean and prioritize README, charts, dashboard, and reports.
