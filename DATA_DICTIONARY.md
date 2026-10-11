# Data Dictionary

This project uses Singapore port, bunker fuel, tanker-arrival, oil-import, Brent crude, and PortWatch-derived regional shipping data.

## Main Processed Tables

### `analysis/output/annual_key_metrics.csv`

| Field | Meaning |
|---|---|
| `year` | Calendar year. |
| `months_observed` | Number of monthly observations available in that year. |
| `complete_year` | Whether all 12 months are available. 2026 is partial in the current data. |
| `cargo_throughput` | Annual total cargo throughput at the Port of Singapore. |
| `container_throughput` | Annual total container throughput. |
| `bunker_sales` | Annual total bunker fuel sales. |
| `number_of_tankers` | Annual tanker arrivals. Available from 2002. |
| `tanker_gross_tonnage` | Annual tanker gross tonnage. Available from 2002. |
| `vessel_calls` | Annual vessel calls over 75 GT, summed across purpose types. |
| `vessel_gross_tonnage` | Annual gross tonnage of vessel calls over 75 GT. |
| `brent_price_usd` | Average Brent crude price for the year. |
| `cargo_per_vessel_call` | Cargo throughput divided by vessel calls. |
| `vessel_gt_per_call` | Vessel gross tonnage divided by vessel calls. |
| `bunker_per_vessel_call` | Bunker sales divided by vessel calls. |
| `*_yoy_pct` | Year-over-year percentage change. Partial years are left blank. |

### `analysis/output/bunker_mix_grouped_annual.csv`

| Field | Meaning |
|---|---|
| `year` | Calendar year. |
| `fuel_group` | Grouped fuel category: conventional, low sulphur, bio-blended, LNG, methanol, ammonia. |
| `bunker_sales` | Annual bunker sales for the fuel group. |
| `share_pct` | Share of total annual bunker sales. |

### `analysis/output/iran_hormuz_exposure_annual_shares.csv`

| Field | Meaning |
|---|---|
| `year` | Calendar year. |
| `direct_iran` | Share of oil imports directly from Iran. |
| `hormuz_core_no_large_bypass` | Share from Kuwait, Qatar, and Bahrain. |
| `gulf_with_bypass_capacity` | Share from Saudi Arabia and United Arab Emirates. |
| `near_gulf_not_core` | Share from Oman and Yemen. |
| `regional_se_asia_oceania` | Share from Malaysia, Indonesia, Brunei, and Australia. |
| `asian_refinery_trade` | Share from Korea, Mainland China, India, Japan, Taiwan, and Thailand. |
| `americas` | Share from the United States, Brazil, and other American markets. |
| `gulf_total_ex_oman_yemen` | `hormuz_core_no_large_bypass + gulf_with_bypass_capacity`. |
| `gulf_plus_near` | Gulf total plus Oman and Yemen. |
| `non_gulf_substitutes` | Regional, Asian refinery, and Americas groups combined. |
| `total_oil_import_value` | Total annual oil-import value in the source table's original unit. |

### `analysis/output/twelve_day_vs_2026_brent_windows.csv`

| Field | Meaning |
|---|---|
| `window` | Event window identifier. |
| `label` | Human-readable event window. |
| `start`, `end` | Window dates. |
| `observations` | Number of daily Brent observations. |
| `avg_brent_price_usd` | Average Brent price in the window. |
| `min_brent_price_usd`, `max_brent_price_usd` | Window minimum and maximum Brent prices. |
| `avg_change_vs_own_pre_pct` | Average price change versus that event's own pre-war baseline. |
| `max_change_vs_own_pre_avg_pct` | Maximum price change versus that event's own pre-war baseline average. |

## Raw Data Coverage

| Source | Coverage |
|---|---|
| Brent crude price | 1987-05-20 to 2026-05-01, daily. |
| Singapore oil imports by market | 1988-01 to 2026-03, monthly. |
| Vessel calls over 75 GT | 1993-01 to 2026-03, monthly. |
| Cargo/container throughput and bunker sales | 1995-01 to 2026-03, monthly. |
| Tanker arrivals | 2002-01 to 2026-03, monthly. |
| FetchSeries/PortWatch regional port calls | 2019-01-01 to 2026-05-01, daily. |

## Notes

- 2026 official Singapore port data only covers January to March in the current local dataset.
- Long-run annual conclusions use complete years through 2025.
- FetchSeries/PortWatch workbooks are used as secondary regional context; official Singapore CSV files are the primary source for Singapore conclusions.
