from __future__ import annotations

from pathlib import Path
from html import escape

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "malacca_strait_data_package" / "malacca_strait_data_package"
OFFICIAL = PACKAGE / "data" / "official_data_gov_sg"
RAW = PACKAGE / "raw"
OUT = ROOT / "analysis" / "output"
CHARTS = ROOT / "analysis" / "charts"


def read_csv(name: str) -> pd.DataFrame:
    # 统一用 UTF-8 读取官方 CSV，避免中文环境下编码漂移。
    return pd.read_csv(OFFICIAL / name, encoding="utf-8")


def fmt_num(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:,.{digits}f}"


def fmt_pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}%"


def cagr(start: float, end: float, years: int) -> float:
    return (end / start) ** (1 / years) - 1


def prepare_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)


def build_monthly_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    cargo = read_csv("cargo_throughput_total_monthly.csv")
    container = read_csv("container_throughput_monthly.csv")
    bunker = read_csv("bunker_sales_total_monthly.csv")
    tanker = read_csv("tanker_arrivals_total_monthly.csv")
    vessel = read_csv("vessel_calls_75gt_monthly.csv")

    vessel_total = (
        vessel.groupby("month", as_index=False)
        .agg(
            vessel_calls=("number_of_vessel_calls", "sum"),
            vessel_gross_tonnage=("gross_tonnage", "sum"),
        )
        .sort_values("month")
    )

    panel = (
        cargo.merge(container, on="month", how="outer")
        .merge(bunker, on="month", how="outer")
        .merge(tanker, on="month", how="outer")
        .merge(vessel_total, on="month", how="outer")
    )

    brent = pd.read_csv(RAW / "fred_brent_crude_oil.csv", encoding="utf-8")
    brent["date"] = pd.to_datetime(brent["date"])
    brent["month"] = brent["date"].dt.to_period("M").astype(str)
    brent_monthly = (
        brent.groupby("month", as_index=False)
        .agg(brent_price_usd=("brent_price_usd", "mean"))
        .sort_values("month")
    )
    panel = panel.merge(brent_monthly, on="month", how="left")

    panel["month_dt"] = pd.to_datetime(panel["month"])
    panel["year"] = panel["month_dt"].dt.year
    panel = panel.sort_values("month_dt")

    numeric_cols = [
        "cargo_throughput",
        "container_throughput",
        "bunker_sales",
        "number_of_tankers",
        "gross_tonnage",
        "vessel_calls",
        "vessel_gross_tonnage",
        "brent_price_usd",
    ]
    for col in numeric_cols:
        panel[col] = pd.to_numeric(panel[col], errors="coerce")

    for col in numeric_cols:
        panel[f"{col}_yoy_pct"] = panel[col].pct_change(12) * 100

    panel["cargo_per_vessel_call"] = panel["cargo_throughput"] / panel["vessel_calls"]
    panel["vessel_gt_per_call"] = panel["vessel_gross_tonnage"] / panel["vessel_calls"]
    panel["bunker_per_vessel_call"] = panel["bunker_sales"] / panel["vessel_calls"]
    panel["bunker_per_vessel_gt"] = panel["bunker_sales"] / panel["vessel_gross_tonnage"]

    def sum_observed(series: pd.Series) -> float:
        # 某些指标起始年份较晚，全缺失年份应保留为空值，而不是汇总成 0。
        return series.sum(min_count=1)

    annual = (
        panel.groupby("year", as_index=True)
        .agg(
            months_observed=("month", "count"),
            cargo_throughput=("cargo_throughput", sum_observed),
            container_throughput=("container_throughput", sum_observed),
            bunker_sales=("bunker_sales", sum_observed),
            number_of_tankers=("number_of_tankers", sum_observed),
            tanker_gross_tonnage=("gross_tonnage", sum_observed),
            vessel_calls=("vessel_calls", sum_observed),
            vessel_gross_tonnage=("vessel_gross_tonnage", sum_observed),
            brent_price_usd=("brent_price_usd", "mean"),
        )
        .reset_index()
    )
    annual["complete_year"] = annual["months_observed"] == 12
    annual["cargo_per_vessel_call"] = annual["cargo_throughput"] / annual["vessel_calls"]
    annual["vessel_gt_per_call"] = annual["vessel_gross_tonnage"] / annual["vessel_calls"]
    annual["bunker_per_vessel_call"] = annual["bunker_sales"] / annual["vessel_calls"]
    annual["bunker_per_vessel_gt"] = annual["bunker_sales"] / annual["vessel_gross_tonnage"]

    annual = annual.sort_values("year")
    for col in [
        "cargo_throughput",
        "container_throughput",
        "bunker_sales",
        "number_of_tankers",
        "tanker_gross_tonnage",
        "vessel_calls",
        "vessel_gross_tonnage",
    ]:
        annual[f"{col}_yoy_pct"] = annual[col].pct_change() * 100
        annual.loc[~annual["complete_year"], f"{col}_yoy_pct"] = np.nan

    return panel, annual


def build_bunker_mix() -> tuple[pd.DataFrame, pd.DataFrame]:
    bunker = read_csv("bunker_sales_breakdown_monthly.csv")
    bunker["month_dt"] = pd.to_datetime(bunker["month"])
    bunker["year"] = bunker["month_dt"].dt.year
    annual = (
        bunker.groupby(["year", "bunker_type"], as_index=False)
        .agg(bunker_sales=("bunker_sales", "sum"))
        .sort_values(["year", "bunker_sales"], ascending=[True, False])
    )
    totals = annual.groupby("year")["bunker_sales"].transform("sum")
    annual["share_pct"] = annual["bunker_sales"] / totals * 100

    def group_fuel(name: str) -> str:
        if name.startswith("Bio-Blended") or name == "B100":
            return "Bio-blended"
        if name in {"LNG", "Methanol", "Ammonia"}:
            return name
        if "Low Sulphur" in name or "Ultra Low Sulphur" in name:
            return "Low sulphur"
        return "Conventional"

    annual["fuel_group"] = annual["bunker_type"].map(group_fuel)
    grouped = (
        annual.groupby(["year", "fuel_group"], as_index=False)
        .agg(bunker_sales=("bunker_sales", "sum"))
        .sort_values(["year", "fuel_group"])
    )
    grouped["share_pct"] = grouped["bunker_sales"] / grouped.groupby("year")["bunker_sales"].transform("sum") * 100
    return annual, grouped


def parse_oil_month(raw: str) -> pd.Timestamp:
    # 官方宽表列名形如 2026Mar，转成长表月份。
    return pd.to_datetime(raw, format="%Y%b", errors="coerce")


def build_oil_imports() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    imports = read_csv("merchandise_imports_oil_by_market_monthly.csv")
    long = imports.melt(id_vars="DataSeries", var_name="month_raw", value_name="oil_import_value")
    long = long.rename(columns={"DataSeries": "market"})
    long["month_dt"] = long["month_raw"].map(parse_oil_month)
    long = long.dropna(subset=["month_dt"]).copy()
    long["month"] = long["month_dt"].dt.to_period("M").astype(str)
    long["year"] = long["month_dt"].dt.year
    long["oil_import_value"] = pd.to_numeric(long["oil_import_value"], errors="coerce").fillna(0)

    annual_market = (
        long.groupby(["year", "market"], as_index=False)
        .agg(oil_import_value=("oil_import_value", "sum"))
        .sort_values(["year", "oil_import_value"], ascending=[True, False])
    )
    annual_total = annual_market.groupby("year", as_index=False).agg(total_oil_import_value=("oil_import_value", "sum"))
    annual_market = annual_market.merge(annual_total, on="year", how="left")
    annual_market["share_pct"] = annual_market["oil_import_value"] / annual_market["total_oil_import_value"] * 100
    annual_market["rank"] = annual_market.groupby("year")["oil_import_value"].rank(method="first", ascending=False)

    concentration = (
        annual_market.assign(share=lambda df: df["oil_import_value"] / df["total_oil_import_value"])
        .groupby("year", as_index=False)
        .agg(
            total_oil_import_value=("oil_import_value", "sum"),
            hhi=("share", lambda s: float((s**2).sum() * 10000)),
            top5_share_pct=("share_pct", lambda s: float(s.nlargest(5).sum())),
            market_count=("market", "count"),
        )
        .sort_values("year")
    )
    return long, annual_market, concentration


def parse_fetchseries_sheet(path: Path, sheet: str, countries: list[str]) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    country_row = df.iloc[0].tolist()
    data = df.iloc[1:].copy()
    out = pd.DataFrame({"date": pd.to_datetime(data.iloc[:, 0], errors="coerce")})
    for country in countries:
        matches = [i for i, value in enumerate(country_row) if str(value) == country]
        if matches:
            out[country] = pd.to_numeric(data[df.columns[matches[0]]], errors="coerce")
    out["year"] = out["date"].dt.year
    return out.dropna(subset=["date"])


def build_regional_port_calls() -> pd.DataFrame:
    path = RAW / "fetchseries_port_calls_by_country_fsr.xlsx"
    countries = ["World", "Singapore", "Malaysia", "Indonesia", "China", "Japan", "Korea"]
    frames = []
    for sheet in ["All cargo vessels", "Container ships", "Tankers"]:
        parsed = parse_fetchseries_sheet(path, sheet, countries)
        annual = parsed.groupby("year", as_index=False)[countries].sum()
        annual["ship_group"] = sheet
        for country in countries:
            base_2019 = annual.loc[annual["year"] == 2019, country].iloc[0]
            annual[f"{country}_index_2019"] = annual[country] / base_2019 * 100
        frames.append(annual)
    return pd.concat(frames, ignore_index=True)


def write_outputs(
    monthly_panel: pd.DataFrame,
    annual: pd.DataFrame,
    bunker_mix: pd.DataFrame,
    bunker_grouped: pd.DataFrame,
    oil_long: pd.DataFrame,
    oil_market: pd.DataFrame,
    oil_concentration: pd.DataFrame,
    regional: pd.DataFrame,
) -> None:
    monthly_panel.to_csv(OUT / "monthly_panel.csv", index=False, encoding="utf-8-sig")
    annual.to_csv(OUT / "annual_key_metrics.csv", index=False, encoding="utf-8-sig")
    bunker_mix.to_csv(OUT / "bunker_mix_annual.csv", index=False, encoding="utf-8-sig")
    bunker_grouped.to_csv(OUT / "bunker_mix_grouped_annual.csv", index=False, encoding="utf-8-sig")
    oil_long.to_csv(OUT / "oil_imports_long.csv", index=False, encoding="utf-8-sig")
    oil_market.to_csv(OUT / "oil_import_market_shares_annual.csv", index=False, encoding="utf-8-sig")
    oil_concentration.to_csv(OUT / "oil_import_concentration_annual.csv", index=False, encoding="utf-8-sig")
    regional.to_csv(OUT / "regional_port_calls_annual.csv", index=False, encoding="utf-8-sig")


PALETTE = [
    "#2364aa",
    "#3da5d9",
    "#73bfb8",
    "#fec601",
    "#ea7317",
    "#7d5fff",
    "#5f0f40",
    "#9a031e",
    "#0f4c5c",
    "#bc6c25",
]


def svg_text(x: float, y: float, text: str, size: int = 12, anchor: str = "middle", weight: str = "400") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Microsoft YaHei, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#222">{escape(text)}</text>'
    )


def write_line_svg(path: Path, title: str, series: list[dict[str, object]], y_label: str = "Index") -> None:
    # 直接生成 SVG，避免依赖额外绘图库。
    width, height = 980, 560
    left, right, top, bottom = 80, 210, 60, 70
    plot_w, plot_h = width - left - right, height - top - bottom
    all_x = [x for item in series for x in item["x"]]
    all_y = [y for item in series for y in item["y"] if pd.notna(y)]
    x_min, x_max = min(all_x), max(all_x)
    y_min = min(0, float(min(all_y)) * 0.95)
    y_max = float(max(all_y)) * 1.08

    def sx(x: float) -> float:
        return left + (x - x_min) / (x_max - x_min) * plot_w

    def sy(y: float) -> float:
        return top + (y_max - y) / (y_max - y_min) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, title, 20, weight="700"),
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#333"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#333"/>',
    ]

    for tick in np.linspace(y_min, y_max, 6):
        y = sy(float(tick))
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        parts.append(svg_text(left - 10, y + 4, f"{tick:.0f}", 11, anchor="end"))

    step = max(1, round((x_max - x_min) / 8))
    year_ticks = list(range(int(x_min), int(x_max) + 1, step))
    if int(x_max) not in year_ticks:
        year_ticks.append(int(x_max))
    for year in year_ticks:
        x = sx(year)
        parts.append(f'<line x1="{x:.1f}" y1="{top + plot_h}" x2="{x:.1f}" y2="{top + plot_h + 5}" stroke="#333"/>')
        parts.append(svg_text(x, top + plot_h + 22, str(year), 11))
    parts.append(svg_text(28, top + plot_h / 2, y_label, 12))

    for idx, item in enumerate(series):
        color = str(item.get("color", PALETTE[idx % len(PALETTE)]))
        dash = str(item.get("dash", ""))
        points = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(item["x"], item["y"]) if pd.notna(y))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.4"{dash_attr}/>')
        legend_y = top + 25 + idx * 24
        parts.append(
            f'<line x1="{left + plot_w + 25}" y1="{legend_y}" x2="{left + plot_w + 50}" '
            f'y2="{legend_y}" stroke="{color}" stroke-width="3"{dash_attr}/>'
        )
        parts.append(svg_text(left + plot_w + 58, legend_y + 4, str(item["name"]), 12, anchor="start"))

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_stacked_bar_svg(path: Path, title: str, data: pd.DataFrame, y_label: str = "Share (%)") -> None:
    width, height = 980, 560
    left, right, top, bottom = 80, 230, 60, 70
    plot_w, plot_h = width - left - right, height - top - bottom
    years = list(data.index)
    cols = list(data.columns)
    max_total = max(100, float(data.sum(axis=1).max()))
    bar_gap = 18
    bar_w = (plot_w - bar_gap * (len(years) - 1)) / len(years)

    def sy(value: float) -> float:
        return top + (max_total - value) / max_total * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, title, 20, weight="700"),
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#333"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#333"/>',
    ]

    for tick in np.linspace(0, max_total, 6):
        y = sy(float(tick))
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        parts.append(svg_text(left - 10, y + 4, f"{tick:.0f}", 11, anchor="end"))
    parts.append(svg_text(28, top + plot_h / 2, y_label, 12))

    for i, year in enumerate(years):
        x = left + i * (bar_w + bar_gap)
        cumulative = 0.0
        for j, col in enumerate(cols):
            value = float(data.loc[year, col])
            if value <= 0:
                continue
            y_top = sy(cumulative + value)
            y_bottom = sy(cumulative)
            parts.append(
                f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w:.1f}" height="{(y_bottom - y_top):.1f}" '
                f'fill="{PALETTE[j % len(PALETTE)]}"/>'
            )
            cumulative += value
        parts.append(svg_text(x + bar_w / 2, top + plot_h + 22, str(year), 11))

    for j, col in enumerate(cols):
        legend_y = top + 24 + j * 24
        parts.append(
            f'<rect x="{left + plot_w + 25}" y="{legend_y - 10}" width="16" height="16" '
            f'fill="{PALETTE[j % len(PALETTE)]}"/>'
        )
        parts.append(svg_text(left + plot_w + 48, legend_y + 3, str(col), 12, anchor="start"))

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def make_charts(annual: pd.DataFrame, bunker_grouped: pd.DataFrame, oil_market: pd.DataFrame, regional: pd.DataFrame) -> None:
    full = annual[(annual["complete_year"]) & (annual["year"] >= 1995) & (annual["year"] <= 2025)].copy()
    index_cols = {
        "cargo_throughput": "Cargo throughput",
        "container_throughput": "Container throughput",
        "bunker_sales": "Bunker sales",
        "vessel_calls": "Vessel calls",
        "vessel_gross_tonnage": "Vessel gross tonnage",
    }
    line_series = []
    for idx, (col, label) in enumerate(index_cols.items()):
        line_series.append(
            {
                "name": label,
                "x": full["year"].tolist(),
                "y": (full[col] / full[col].iloc[0] * 100).tolist(),
                "color": PALETTE[idx],
            }
        )
    write_line_svg(CHARTS / "singapore_maritime_index.svg", "Singapore maritime indicators, 1995=100", line_series)

    recent_mix = bunker_grouped[(bunker_grouped["year"] >= 2019) & (bunker_grouped["year"] <= 2025)]
    mix_pivot = recent_mix.pivot(index="year", columns="fuel_group", values="share_pct").fillna(0)
    desired = [col for col in ["Conventional", "Low sulphur", "Bio-blended", "LNG", "Methanol", "Ammonia"] if col in mix_pivot.columns]
    mix_pivot = mix_pivot[desired]
    write_stacked_bar_svg(CHARTS / "bunker_fuel_mix_share.svg", "Bunker fuel mix by annual share", mix_pivot)

    selected_years = [1995, 2002, 2008, 2019, 2025]
    top_market = oil_market[oil_market["year"].isin(selected_years) & (oil_market["rank"] <= 5)].copy()
    top_market["label"] = top_market["market"].where(top_market["market"].str.len() <= 20, top_market["market"].str.slice(0, 18) + "...")
    pivot = top_market.pivot_table(index="year", columns="label", values="share_pct", aggfunc="sum").fillna(0)
    write_stacked_bar_svg(CHARTS / "oil_import_top_market_shares.svg", "Top oil-import market shares", pivot)

    reg = regional[(regional["ship_group"].isin(["All cargo vessels", "Tankers"])) & (regional["year"].between(2019, 2025))]
    dashes = {"Singapore": "", "Malaysia": "8 5", "Indonesia": "2 4", "World": "10 4 2 4"}
    line_series = []
    color_idx = 0
    for group in ["All cargo vessels", "Tankers"]:
        subset = reg[reg["ship_group"] == group]
        for country in ["Singapore", "Malaysia", "Indonesia", "World"]:
            col = f"{country}_index_2019"
            label = f"{country} {group.replace(' vessels', '')}"
            line_series.append(
                {
                    "name": label,
                    "x": subset["year"].tolist(),
                    "y": subset[col].tolist(),
                    "color": PALETTE[color_idx % len(PALETTE)],
                    "dash": dashes[country],
                }
            )
            color_idx += 1
    write_line_svg(
        CHARTS / "regional_port_calls_index.svg",
        "Regional port-call index from FetchSeries/PortWatch, 2019=100",
        line_series,
    )


def generate_report(annual: pd.DataFrame, bunker_mix: pd.DataFrame, bunker_grouped: pd.DataFrame, oil_market: pd.DataFrame, oil_concentration: pd.DataFrame, regional: pd.DataFrame) -> str:
    full = annual[annual["complete_year"]].set_index("year")
    y1995 = full.loc[1995]
    y2019 = full.loc[2019]
    y2020 = full.loc[2020]
    y2025 = full.loc[2025]
    peak_cargo_year = int(full["cargo_throughput"].idxmax())
    peak_cargo = full.loc[peak_cargo_year, "cargo_throughput"]

    def growth(col: str, start_year: int, end_year: int) -> float:
        return (full.loc[end_year, col] / full.loc[start_year, col] - 1) * 100

    fuel_2019 = bunker_mix[(bunker_mix["year"] == 2019)].set_index("bunker_type")
    fuel_2020 = bunker_mix[(bunker_mix["year"] == 2020)].set_index("bunker_type")
    fuel_2025 = bunker_mix[(bunker_mix["year"] == 2025)].set_index("bunker_type")
    group_2024 = bunker_grouped[bunker_grouped["year"] == 2024].set_index("fuel_group")
    group_2025 = bunker_grouped[bunker_grouped["year"] == 2025].set_index("fuel_group")

    oil_conc = oil_concentration.set_index("year")
    oil_1995 = oil_market[(oil_market["year"] == 1995) & (oil_market["rank"] <= 5)].copy()
    oil_2025 = oil_market[(oil_market["year"] == 2025) & (oil_market["rank"] <= 5)].copy()
    top_1995 = oil_market[(oil_market["year"] == 1995) & (oil_market["rank"] == 1)].iloc[0]
    top_2025 = oil_market[(oil_market["year"] == 2025) & (oil_market["rank"] == 1)].iloc[0]

    reg = regional.set_index(["ship_group", "year"])
    sg_tanker_2025 = reg.loc[("Tankers", 2025), "Singapore_index_2019"]
    my_tanker_2025 = reg.loc[("Tankers", 2025), "Malaysia_index_2019"]
    id_tanker_2025 = reg.loc[("Tankers", 2025), "Indonesia_index_2019"]
    sg_all_2025 = reg.loc[("All cargo vessels", 2025), "Singapore_index_2019"]
    my_all_2025 = reg.loc[("All cargo vessels", 2025), "Malaysia_index_2019"]
    id_all_2025 = reg.loc[("All cargo vessels", 2025), "Indonesia_index_2019"]

    lines = [
        "# 新加坡海运能源枢纽：从“吞吐量增长”到“高吨位与燃料服务”",
        "",
        "## 一句话结论",
        "",
        (
            "1995-2025 年，新加坡港的核心变化不是船舶到港次数暴涨，而是服务对象变得更大、"
            "能源补给更集中、燃料和油品来源结构更复杂。货物吞吐量约翻一倍，集装箱吞吐量和船用燃料销售约增长三倍，"
            "但船舶到港次数只增长约五分之一；与此同时，靠港船舶总吨位增长近五倍。这说明新加坡的枢纽价值更多来自"
            "大船、高频补给、能源中转和燃料供应能力，而不是简单的“船更多”。"
        ),
        "",
        "## 数据与清洗口径",
        "",
        "- 主数据使用 `data/official_data_gov_sg/` 下的官方月度 CSV：货物吞吐量、集装箱吞吐量、船舶到港、油轮到港、船用燃料销售和油品进口市场。",
        "- Brent 油价使用 `raw/fred_brent_crude_oil.csv`，由日度均值聚合到月度。",
        "- `merchandise_imports_oil_by_market_monthly.csv` 是市场为行、月份为列的宽表，已清洗成长表并计算年度市场份额、Top 5 份额和 HHI 集中度。",
        "- `fetchseries_port_calls_by_country_fsr.xlsx` 仅用作区域背景对照，主结论仍以官方新加坡月度数据为准。",
        "- 2026 年官方港口数据只到 3 月，FRED 油价到 5 月，因此年度同比和峰值判断只使用 2025 年及之前的完整年份。",
        "",
        "## 证据 1：规模扩张主要来自大船化，而不是到港次数",
        "",
        (
            f"1995 到 2025 年，货物吞吐量从 {fmt_num(y1995['cargo_throughput'])} 增至 {fmt_num(y2025['cargo_throughput'])}，"
            f"增长 {fmt_pct(growth('cargo_throughput', 1995, 2025))}，年化约 {fmt_pct(cagr(y1995['cargo_throughput'], y2025['cargo_throughput'], 30) * 100)}。"
            f"集装箱吞吐量从 {fmt_num(y1995['container_throughput'])} 增至 {fmt_num(y2025['container_throughput'])}，"
            f"增长 {fmt_pct(growth('container_throughput', 1995, 2025))}，年化约 {fmt_pct(cagr(y1995['container_throughput'], y2025['container_throughput'], 30) * 100)}。"
        ),
        (
            f"同一时期，船舶到港次数只从 {fmt_num(y1995['vessel_calls'], 0)} 增至 {fmt_num(y2025['vessel_calls'], 0)}，"
            f"增长 {fmt_pct(growth('vessel_calls', 1995, 2025))}；但到港船舶总吨位从 {fmt_num(y1995['vessel_gross_tonnage'])} "
            f"增至 {fmt_num(y2025['vessel_gross_tonnage'])}，增长 {fmt_pct(growth('vessel_gross_tonnage', 1995, 2025))}。"
        ),
        (
            f"因此，每次到港对应的平均总吨位从 {fmt_num(y1995['vessel_gt_per_call'], 2)} 增至 "
            f"{fmt_num(y2025['vessel_gt_per_call'], 2)}，约为 1995 年的 {fmt_num(y2025['vessel_gt_per_call'] / y1995['vessel_gt_per_call'], 2)} 倍。"
            f"2025 年集装箱吞吐量、船用燃料销售和船舶总吨位均达到完整年份样本峰值；货物吞吐量的峰值在 {peak_cargo_year} 年，"
            f"2025 年仍为峰值的 {fmt_pct(y2025['cargo_throughput'] / peak_cargo * 100)}。"
        ),
        "",
        "## 证据 2：疫情冲击下，燃料补给比普通到港更有韧性",
        "",
        (
            f"2020 年是结构差异最清楚的一年：总船舶到港次数同比下降 {fmt_pct(abs(y2020['vessel_calls_yoy_pct']))}，"
            f"货物吞吐量下降 {fmt_pct(abs(y2020['cargo_throughput_yoy_pct']))}，但船用燃料销售同比增长 "
            f"{fmt_pct(y2020['bunker_sales_yoy_pct'])}，油轮到港次数增长 {fmt_pct(y2020['number_of_tankers_yoy_pct'])}，"
            f"油轮总吨位增长 {fmt_pct(y2020['tanker_gross_tonnage_yoy_pct'])}。"
        ),
        (
            f"这说明当普通靠港活动受冲击时，新加坡的能源航运服务仍保持强度。2020 年每次到港对应的船用燃料销售从 2019 年的 "
            f"{fmt_num(y2019['bunker_per_vessel_call'], 3)} 升至 {fmt_num(y2020['bunker_per_vessel_call'], 3)}，"
            "不是因为所有活动都扩张，而是因为留下来的船舶和业务更偏向大吨位、油轮与补给需求。"
        ),
        "",
        "## 证据 3：燃料结构在 2020 年发生断点，随后替代燃料开始出现",
        "",
        (
            f"2019 年，Marine Fuel Oil 仍占船用燃料销售的 {fmt_pct(fuel_2019.loc['Marine Fuel Oil', 'share_pct'])}，"
            f"Low Sulphur Fuel Oil 占 {fmt_pct(fuel_2019.loc['Low Sulphur Fuel Oil', 'share_pct'])}。到 2020 年，"
            f"Low Sulphur Fuel Oil 跃升到 {fmt_pct(fuel_2020.loc['Low Sulphur Fuel Oil', 'share_pct'])}，"
            f"Marine Fuel Oil 降至 {fmt_pct(fuel_2020.loc['Marine Fuel Oil', 'share_pct'])}。"
        ),
        (
            f"到 2025 年，Low Sulphur Fuel Oil 仍为第一大类，占 {fmt_pct(fuel_2025.loc['Low Sulphur Fuel Oil', 'share_pct'])}；"
            f"Marine Fuel Oil 回升到 {fmt_pct(fuel_2025.loc['Marine Fuel Oil', 'share_pct'])}，说明低硫化不是简单替代全部传统燃油，"
            "而是形成多燃料并存。"
        ),
        (
            f"更小但值得跟踪的是新燃料：Bio-blended 组在 2024 年占 {fmt_pct(group_2024.loc['Bio-blended', 'share_pct'])}，"
            f"2025 年升至 {fmt_pct(group_2025.loc['Bio-blended', 'share_pct'])}；LNG 从 2024 年的 "
            f"{fmt_pct(group_2024.loc['LNG', 'share_pct'])} 升至 2025 年的 {fmt_pct(group_2025.loc['LNG', 'share_pct'])}。"
            "这些份额仍小，但它们显示新加坡港已经不只是卖油量，而是在形成替代燃料供给能力。"
        ),
        "",
        "## 证据 4：油品进口来源从高度集中转向多中心",
        "",
        (
            f"1995 年油品进口市场高度集中：Top 5 市场合计占 {fmt_pct(oil_conc.loc[1995, 'top5_share_pct'])}，"
            f"HHI 为 {fmt_num(oil_conc.loc[1995, 'hhi'], 0)}；第一来源是 {top_1995['market']}，占 "
            f"{fmt_pct(top_1995['share_pct'])}。"
        ),
        (
            f"到 2025 年，Top 5 合计降至 {fmt_pct(oil_conc.loc[2025, 'top5_share_pct'])}，HHI 降至 "
            f"{fmt_num(oil_conc.loc[2025, 'hhi'], 0)}；第一来源变为 {top_2025['market']}，占 "
            f"{fmt_pct(top_2025['share_pct'])}。"
        ),
        "1995 年 Top 5 来源："
        + "、".join([f"{row.market} {fmt_pct(row.share_pct)}" for row in oil_1995.itertuples()]),
        "2025 年 Top 5 来源："
        + "、".join([f"{row.market} {fmt_pct(row.share_pct)}" for row in oil_2025.itertuples()]),
        "",
        "## 区域对照：新加坡更像成熟高服务密度节点",
        "",
        (
            "FetchSeries/PortWatch 的日度港口到港数据给出一个背景：2019-2025 年，"
            f"新加坡全部货船到港指数从 100 升至 {fmt_num(sg_all_2025, 1)}，马来西亚升至 {fmt_num(my_all_2025, 1)}，"
            f"印尼升至 {fmt_num(id_all_2025, 1)}；油轮到港指数中新加坡为 {fmt_num(sg_tanker_2025, 1)}，"
            f"马来西亚为 {fmt_num(my_tanker_2025, 1)}，印尼为 {fmt_num(id_tanker_2025, 1)}。"
        ),
        (
            "这意味着区域内新增到港增长并不全部集中在新加坡；新加坡的优势更像成熟枢纽：到港增长温和，"
            "但总吨位、燃料销售和多燃料服务能力更强。"
        ),
        "",
        "## 故事判断",
        "",
        "这组数据支持一个合理的数据故事：",
        "",
        "1. 新加坡港的长期增长不是靠单纯增加船数，而是靠更大船舶、更高总吨位和更强补给服务。",
        "2. 能源航运业务在冲击期更有韧性，2020 年普通到港明显下降，但油轮和燃料销售仍上升。",
        "3. 2020 年以后，燃料结构从传统 Marine Fuel Oil 主导转向低硫燃料主导，近年开始出现生物混合燃料、LNG、甲醇等小份额新燃料。",
        "4. 油品进口来源从 1990 年代中东高度集中，转向 2020 年代的中东、东南亚、东北亚、美洲等多中心结构。",
        "",
        "因此，如果要把这个项目讲成论文或简历项目，题目可以是：**新加坡海运能源枢纽的结构升级：大船化、燃料转型与进口来源多元化**。",
        "",
        "## 输出文件",
        "",
        "- 清洗后的月度面板：`analysis/output/monthly_panel.csv`",
        "- 年度关键指标：`analysis/output/annual_key_metrics.csv`",
        "- 船用燃料结构：`analysis/output/bunker_mix_annual.csv` 与 `analysis/output/bunker_mix_grouped_annual.csv`",
        "- 油品进口长表与市场份额：`analysis/output/oil_imports_long.csv`、`analysis/output/oil_import_market_shares_annual.csv`、`analysis/output/oil_import_concentration_annual.csv`",
        "- 区域港口到港对照：`analysis/output/regional_port_calls_annual.csv`",
        "- 图表：`analysis/charts/singapore_maritime_index.svg`、`analysis/charts/bunker_fuel_mix_share.svg`、`analysis/charts/oil_import_top_market_shares.svg`、`analysis/charts/regional_port_calls_index.svg`",
    ]
    report = "\n".join(lines) + "\n"
    (OUT / "singapore_maritime_energy_story.md").write_text(report, encoding="utf-8")
    return report


def main() -> None:
    prepare_dirs()
    monthly_panel, annual = build_monthly_panel()
    bunker_mix, bunker_grouped = build_bunker_mix()
    oil_long, oil_market, oil_concentration = build_oil_imports()
    regional = build_regional_port_calls()

    write_outputs(
        monthly_panel,
        annual,
        bunker_mix,
        bunker_grouped,
        oil_long,
        oil_market,
        oil_concentration,
        regional,
    )
    make_charts(annual, bunker_grouped, oil_market, regional)
    report = generate_report(annual, bunker_mix, bunker_grouped, oil_market, oil_concentration, regional)
    print(report)


if __name__ == "__main__":
    main()
