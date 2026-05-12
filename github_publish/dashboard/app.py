from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "output"
CHARTS = ROOT / "analysis" / "charts"


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    # 输出表统一用 UTF-8-SIG 保存，兼容 Excel 和中文环境。
    return pd.read_csv(OUT / name, encoding="utf-8-sig")


def show_svg(name: str, caption: str) -> None:
    path = CHARTS / name
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(f"Chart not found: {name}")


def metric_delta(current: float, previous: float) -> str:
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return "NA"
    return f"{(current / previous - 1) * 100:.1f}%"


def main() -> None:
    st.set_page_config(
        page_title="Singapore Maritime Energy Analytics",
        page_icon="🚢",
        layout="wide",
    )

    st.title("Singapore Maritime Energy Analytics")
    st.caption("Port growth, bunker fuel transition, and Iran/Hormuz risk transmission")

    annual = load_csv("annual_key_metrics.csv")
    q1 = load_csv("iran_hormuz_exposure_q1_shares.csv").set_index("year")
    brent_events = load_csv("twelve_day_vs_2026_brent_windows.csv")
    official_impact = load_csv("us_iran_official_q1_impact.csv").set_index("metric")

    y1995 = annual.loc[annual["year"] == 1995].iloc[0]
    y2025 = annual.loc[annual["year"] == 2025].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cargo throughput growth", metric_delta(y2025["cargo_throughput"], y1995["cargo_throughput"]))
    c2.metric("Vessel gross tonnage growth", metric_delta(y2025["vessel_gross_tonnage"], y1995["vessel_gross_tonnage"]))
    c3.metric("2025 Gulf oil-import share", f"{q1.loc[2025, 'gulf_total_ex_oman_yemen']:.1f}% Q1")
    c4.metric("2026Q1 Gulf oil-import share", f"{q1.loc[2026, 'gulf_total_ex_oman_yemen']:.1f}%")

    tab1, tab2, tab3, tab4 = st.tabs(["Port System", "Fuel Transition", "War Events", "Hormuz Exposure"])

    with tab1:
        st.subheader("Long-run port transformation")
        show_svg("singapore_maritime_index.svg", "Singapore maritime indicators, 1995=100")
        st.dataframe(
            annual[
                [
                    "year",
                    "cargo_throughput",
                    "container_throughput",
                    "bunker_sales",
                    "vessel_calls",
                    "vessel_gross_tonnage",
                ]
            ].tail(12),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.subheader("Bunker fuel mix")
        show_svg("bunker_fuel_mix_share.svg", "Annual bunker fuel mix")
        bunker = load_csv("bunker_mix_grouped_annual.csv")
        pivot = bunker.pivot(index="year", columns="fuel_group", values="share_pct").fillna(0)
        st.line_chart(pivot[pivot.index >= 2019])

    with tab3:
        st.subheader("Event-window comparison")
        show_svg("brent_event_comparison.svg", "Brent price shocks")
        st.write(
            "The 2025 Twelve-Day War mainly produced a short risk-premium spike. "
            "The 2026 Hormuz crisis produced a larger and more persistent supply-chain shock."
        )
        st.dataframe(brent_events, use_container_width=True, hide_index=True)
        st.write("2026Q1 official port indicators:")
        st.dataframe(official_impact.reset_index(), use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("Iran/Hormuz exposure")
        show_svg("hormuz_exposure_annual.svg", "Oil-import exposure by source group")
        show_svg("q1_2026_gulf_reallocation.svg", "2026Q1 source reallocation")
        monthly = load_csv("iran_hormuz_exposure_recent_monthly.csv").set_index("month")
        st.line_chart(
            monthly[
                [
                    "gulf_total_ex_oman_yemen",
                    "gulf_with_bypass_capacity",
                    "non_gulf_substitutes",
                ]
            ]
        )

    with st.expander("Project reports"):
        st.markdown(
            """
            - `analysis/output/singapore_maritime_energy_story.md`
            - `analysis/output/twelve_day_vs_2026_comparison.md`
            - `analysis/output/iran_hormuz_exposure_story.md`
            """
        )


if __name__ == "__main__":
    main()
