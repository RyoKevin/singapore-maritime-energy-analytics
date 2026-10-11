# Singapore Maritime Energy Analytics

A reproducible **portfolio presentation of published outputs** on Singapore's maritime-energy hub, port growth, bunker-fuel mix and exposure to Gulf supply chains.

**[Live interactive data story](https://ryokevin.github.io/singapore-maritime-energy-analytics/)** · [Source HTML](docs/interactive.html) · [Static charts](docs/index.html) · [Data dictionary](DATA_DICTIONARY.md) · [Methodology and limitations](METHODOLOGY.md)

> The repository includes analytical scripts, selected processed CSVs and generated charts. **It does not include the original raw data package**, so the complete pipeline cannot yet be rerun from a fresh clone. The interactive HTML page embeds precomputed data and can be inspected without the raw package. These results represent a May 2026 snapshot, **not live data**.

## Key descriptive findings

| Indicator | Dataset result |
|---|---|
| Vessel calls, 1995–2025 | +21.8% |
| Vessel gross tonnage, 1995–2025 | +485.5% |
| Share of Singapore oil-import **value** from the defined Gulf markets, full-year 2025 | 36.0% |
| Share from the same Gulf markets, 2025Q1 → 2026Q1 | 29.6% → 38.8% |
| Brent mean, 2026 shock window relative to pre-event window | +50.1% (descriptive difference) |

Import-origin shares measure **trade value by reported partner**, not physical passage through the Strait of Hormuz. Q1 2026 includes January and most of February **before** the February 28 conflict onset; its year-over-year difference is **not a causal estimate of conflict effects**. Changes in Brent or port calls are unadjusted event-window contrasts. See [METHODOLOGY.md](METHODOLOGY.md).

## Explore

- [Interactive ECharts story](docs/interactive.html): browser-ready, precomputed interactive charts; loads ECharts from a CDN.
- [Static summary](docs/index.html): five SVG charts.
- [Long-run Singapore maritime story](analysis/output/singapore_maritime_energy_story.md)
- [Gulf/Hormuz import-origin exposure](analysis/output/iran_hormuz_exposure_story.md)
- [2025/2026 event-window comparison](analysis/output/twelve_day_vs_2026_comparison.md)
- [2026 preliminary port and oil-price observations](analysis/output/us_iran_war_impact.md)

## Repository layout

```text
analysis/                 Python scripts, charts and selected output CSVs
dashboard/app.py          Streamlit dashboard using committed processed tables
docs/                     GitHub Pages static and interactive HTML
DATA_DICTIONARY.md        Variables, units and source coverage
METHODOLOGY.md            Measurement, identification and limitations
tests/                    Self-contained tests of committed outputs
requirements.txt          Runtime dependencies
```

## Run with the committed outputs

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
python -m unittest discover -s tests -v
```

Open `docs/interactive.html` in a browser for the interactive story. To publish via GitHub Pages, configure **Deploy from a branch → main → /docs** after merging the cleanup PR; the resulting URL depends on repository Pages settings. The HTML uses a CDN so a network connection is needed for charts.

## Full source-to-output reproduction (requires missing source files)

The scripts expect `malacca_strait_data_package/malacca_strait_data_package/data/official_data_gov_sg/*.csv` and `malacca_strait_data_package/malacca_strait_data_package/raw/fred_brent_crude_oil.csv` plus `fetchseries_port_calls_by_country_fsr.xlsx`. These files **are not committed**. See [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md) for source descriptions and the expected layout. After obtaining the original matching ZIP snapshot (extract it using the documented commands in [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md)):

```bash
python analysis/run_all.py
```

**Verified local replay (October 11, 2026):** `python analysis/run_all.py` ran successfully using the matching historical ZIP provided by the project owner. It regenerated 24 CSV outputs, 4 reports, 7 analytical SVG charts, and the interactive HTML page. All 7 CSV tables that were previously committed matched numerically (absolute or relative tolerance 1e-11); SVG graphics matched after normalizing line endings. All 8 unittest checks passed with `MARITIME_SOURCE_ZIP` set. The archive remains outside GitHub, so third-party full replay still requires the original data snapshot.

Data origins reported by the author: Maritime and Port Authority of Singapore and Enterprise Singapore datasets via [data.gov.sg](https://data.gov.sg/); Brent price data from a local FRED-derived CSV; secondary regional port-call workbooks derived from IMF PortWatch/FetchSeries. Dataset-level original download URLs and extraction timestamps still need to be documented. The verified historical ZIP has SHA-256 `638fcc38db8afc7c394989679ce19fefa996eeb5ab717d9988402a642dd45301`.

## Scope

The available official Singapore data here end in **March 2026**; the historical Brent snapshot ends **May 1, 2026**. This project is descriptive; it does not establish that geopolitical events caused the observed price, import or shipping changes.
