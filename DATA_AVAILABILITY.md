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

Run selected-output tests using `python -m unittest discover -s tests -v`; run the dashboard using `streamlit run dashboard/app.py`. With matching raw files available, `python analysis/run_all.py` attempts to regenerate outputs. No end-to-end run from a fresh clone is claimed.
