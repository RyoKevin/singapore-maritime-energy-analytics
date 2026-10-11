# Data availability and expected layout

**Current status:** the public repository contains selected output tables and charts, but not the original raw-data bundle used by the analysis scripts. Do not describe the full project as clone-and-run reproducible until the bundle or an automated source acquisition workflow has been added and tested.

Expected project-relative layout:

```text
malacca_strait_data_package/
  malacca_strait_data_package/
    data/official_data_gov_sg/
      cargo_throughput_total_monthly.csv
      container_throughput_monthly.csv
      bunker_sales_total_monthly.csv
      bunker_sales_breakdown_monthly.csv
      tanker_arrivals_total_monthly.csv
      vessel_calls_75gt_monthly.csv
      merchandise_imports_oil_by_market_monthly.csv
    raw/
      fred_brent_crude_oil.csv
      fetchseries_port_calls_by_country_fsr.xlsx
```

Original sources: Singapore MPA and Enterprise Singapore through [data.gov.sg](https://data.gov.sg/); a local FRED-derived Brent daily series; secondary FetchSeries/IMF PortWatch regional vessel-arrival workbooks. These filenames are **local cleaned input contracts**; downloading contemporary files may require column harmonization and will not recreate the historical May 2026 snapshot verbatim. Exact dataset IDs, URLs, extraction dates, and redistribution rights are pending documentation. No data were fabricated to close this gap.

Run selected-output tests using `python -m unittest discover -s tests -v`; run the dashboard using `streamlit run dashboard/app.py`. With matching raw files available, `python analysis/run_all.py` attempts to regenerate outputs. The full `analysis/run_all.py` pipeline was successfully replayed locally on October 11, 2026 with the matching ZIP; public CI runs Python syntax and published-output tests without storing the raw archive. A third party still needs the same historical source snapshot for full reproduction.

## Verified source archive and reproducibility

The original matching source snapshot was provided separately as `malacca_strait_data_package.zip` (64,405,809 bytes); the ZIP integrity check passed, and all seven expected official Singapore CSVs, the Brent CSV and the relevant PortWatch/FetchSeries workbook are present. The ZIP is **not** checked into this public repository.

To use it, place the ZIP in the repository root and run:

```bash
python -m zipfile -e malacca_strait_data_package.zip .
python -m unittest discover -s tests -v
python analysis/run_all.py
```

The extraction path is deliberately nested twice and matches the existing scripts. These commands require the runtime dependencies and the matching source snapshot. Recomputing from the complete raw bundle was verified locally on October 11, 2026, using Python 3.13; the public CI run validates code syntax and published outputs only. The ZIP SHA-256 is `638fcc38db8afc7c394989679ce19fefa996eeb5ab717d9988402a642dd45301`.

### Official Singapore dataset IDs recorded in the source package

| Cleaned filename (without .csv) | data.gov.sg dataset ID |
|---|---|
| cargo_throughput_total_monthly | d_042dd8b935eab998f389adaf559c80de |
| container_throughput_monthly | d_da030f7028200d19ffcbe4a2d71af39c |
| vessel_calls_75gt_monthly | d_48cb38d12697d3463c8cadfb22e6c61d |
| tanker_arrivals_total_monthly | d_9adb5ace517591edd9a8c88291ac1f1c |
| bunker_sales_total_monthly | d_89d2874dad74a273270369334f1e7d28 |
| bunker_sales_breakdown_monthly | d_4f5abbf4486bf8e52bbed3be56dde562 |
| merchandise_imports_oil_by_market_monthly | d_d8436b391529c6be9da001ffc7f19e51 |

The source archive also provides `scripts/download_data.py`, which references data.gov.sg's download APIs, FRED, and FetchSeries/PortWatch links. Fresh downloads may differ from this historical snapshot; in particular, the downloader does not automatically create the exact local `fred_brent_crude_oil.csv` schema used here.
