# Methodology and interpretation

## Measurement

Singapore port indicators come from monthly official datasets. The 1995–2025 growth comparisons use complete calendar years. Vessel calls, vessel gross tonnage, container throughput, bunker sales and oil-import **values** are different measures; ratios per call are descriptive intensity metrics, not proof of an individual vessel's size or activity.

The import-origin grouping is a **proxy for potential Gulf-related exposure**: Kuwait, Qatar and Bahrain are classified as core; Saudi Arabia and UAE are identified separately as countries with some bypass capacity; Iran is tracked separately; Oman/Yemen are outside the main Gulf aggregate. These classifications apply to reported trade partners and do not show shipping routes, whether oil physically traversed Hormuz, refinery origin or contractual rerouting. The group 'non_gulf_substitutes' is a convenient reporting label, **not verified substitute capacity**.

## Event comparison and identification

- 2025 conflict comparison: pre-window May 1–June 12; event June 13–24; post June 25–July 31.
- 2026 comparison: pre January 1–February 27; shock February 28–March 31; follow-up April 1–May 1.
- Brent statistics are unweighted averages of *available daily observations* in each window. These comparisons are sensitive to window selection, broader oil-market conditions and any missing dates.
- PortWatch/FetchSeries values are descriptive daily port-call indicators and use different definitions from MPA official monthly series. Observed window differences are **not causally identified**.
- Q1 2026 year-over-year import-origin results cover January–March; only March fully follows the February 28 event onset. Do not label the Q1 composition shift as a *wartime response* without analyzing monthly pre-trends and post-event comparisons.
- Import shares are value weighted and can move through **prices, exchange-rate effects, reported origin, or quantities**. The repository does not separate these components.
- The current published outputs represent a historical May 2026 snapshot.

## Further work before causal claims

Obtain monthly April–September 2026 observations and raw transaction-level or quantity/price decomposition; inspect January–February 2026 pre-trends; compare matched prior-year months, peer ports, alternate event windows, pre-trends and relevant seasonality; quantify estimation uncertainty. Even with those checks, causal attribution requires an explicit identification strategy.

## Reproducibility

Committed processed CSVs permit selected descriptive checks and the Streamlit dashboard. A source-to-output build also requires the missing raw official Singapore CSVs, FRED-style Brent CSV and the original PortWatch/FetchSeries workbook, as described in [DATA_AVAILABILITY.md](DATA_AVAILABILITY.md). No current-time updates are implied.
