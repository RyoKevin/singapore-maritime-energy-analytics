from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "malacca_strait_data_package" / "malacca_strait_data_package"
OFFICIAL = PACKAGE / "data" / "official_data_gov_sg"
RAW = PACKAGE / "raw"
OUT = ROOT / "analysis" / "output"


def read_official(name: str) -> pd.DataFrame:
    # 官方数据文件统一按 UTF-8 读取。
    return pd.read_csv(OFFICIAL / name, encoding="utf-8")


def fmt(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:,.{digits}f}"


def pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}%"


def brent_event_windows() -> pd.DataFrame:
    brent = pd.read_csv(RAW / "fred_brent_crude_oil.csv", encoding="utf-8")
    brent["date"] = pd.to_datetime(brent["date"])
    brent["brent_price_usd"] = pd.to_numeric(brent["brent_price_usd"], errors="coerce")
    windows = [
        ("2025Q4_baseline", "2025-10-01", "2025-12-31"),
        ("2026_pre_war", "2026-01-01", "2026-02-27"),
        ("shock_2026-02-28_to_2026-03-31", "2026-02-28", "2026-03-31"),
        ("prolonged_2026-04-01_to_2026-05-01", "2026-04-01", "2026-05-01"),
    ]
    rows = []
    for label, start, end in windows:
        sample = brent[(brent["date"] >= start) & (brent["date"] <= end)].copy()
        rows.append(
            {
                "window": label,
                "start": start,
                "end": end,
                "observations": len(sample),
                "avg_brent_price_usd": sample["brent_price_usd"].mean(),
                "min_brent_price_usd": sample["brent_price_usd"].min(),
                "max_brent_price_usd": sample["brent_price_usd"].max(),
                "first_brent_price_usd": sample["brent_price_usd"].iloc[0] if len(sample) else np.nan,
                "last_brent_price_usd": sample["brent_price_usd"].iloc[-1] if len(sample) else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    pre_avg = out.loc[out["window"] == "2026_pre_war", "avg_brent_price_usd"].iloc[0]
    out["avg_change_vs_pre_war_pct"] = (out["avg_brent_price_usd"] / pre_avg - 1) * 100
    return out


def official_q1_impact() -> pd.DataFrame:
    specs = [
        ("cargo_throughput", "cargo_throughput_total_monthly.csv", "cargo_throughput"),
        ("container_throughput", "container_throughput_monthly.csv", "container_throughput"),
        ("bunker_sales", "bunker_sales_total_monthly.csv", "bunker_sales"),
        ("tanker_arrivals_number", "tanker_arrivals_total_monthly.csv", "number_of_tankers"),
        ("tanker_arrivals_gt", "tanker_arrivals_total_monthly.csv", "gross_tonnage"),
    ]
    rows = []
    for metric, file_name, col in specs:
        data = read_official(file_name)
        data["month_dt"] = pd.to_datetime(data["month"])
        data[col] = pd.to_numeric(data[col], errors="coerce")
        q1_2026 = data[(data["month_dt"] >= "2026-01-01") & (data["month_dt"] <= "2026-03-01")][col].sum()
        q1_2025 = data[(data["month_dt"] >= "2025-01-01") & (data["month_dt"] <= "2025-03-01")][col].sum()
        mar_2026 = data.loc[data["month"] == "2026-03", col].iloc[0]
        mar_2025 = data.loc[data["month"] == "2025-03", col].iloc[0]
        feb_2026 = data.loc[data["month"] == "2026-02", col].iloc[0]
        rows.append(
            {
                "metric": metric,
                "q1_2026": q1_2026,
                "q1_2025": q1_2025,
                "q1_yoy_pct": (q1_2026 / q1_2025 - 1) * 100,
                "mar_2026": mar_2026,
                "mar_2025": mar_2025,
                "mar_yoy_pct": (mar_2026 / mar_2025 - 1) * 100,
                "mar_vs_feb_2026_pct": (mar_2026 / feb_2026 - 1) * 100,
            }
        )
    return pd.DataFrame(rows)


def bunker_q1_mix() -> pd.DataFrame:
    data = read_official("bunker_sales_breakdown_monthly.csv")
    data["month_dt"] = pd.to_datetime(data["month"])
    q1_2026 = (
        data[(data["month_dt"] >= "2026-01-01") & (data["month_dt"] <= "2026-03-01")]
        .groupby("bunker_type", as_index=False)
        .agg(q1_2026_bunker_sales=("bunker_sales", "sum"))
    )
    q1_2025 = (
        data[(data["month_dt"] >= "2025-01-01") & (data["month_dt"] <= "2025-03-01")]
        .groupby("bunker_type", as_index=False)
        .agg(q1_2025_bunker_sales=("bunker_sales", "sum"))
    )
    out = q1_2026.merge(q1_2025, on="bunker_type", how="left")
    out["share_2026_pct"] = out["q1_2026_bunker_sales"] / out["q1_2026_bunker_sales"].sum() * 100
    out["q1_yoy_pct"] = (out["q1_2026_bunker_sales"] / out["q1_2025_bunker_sales"] - 1) * 100
    out.loc[out["q1_2025_bunker_sales"].fillna(0) == 0, "q1_yoy_pct"] = np.nan
    return out.sort_values("q1_2026_bunker_sales", ascending=False)


def oil_imports_q1() -> pd.DataFrame:
    data = read_official("merchandise_imports_oil_by_market_monthly.csv")
    month_cols = ["2026Jan", "2026Feb", "2026Mar", "2025Jan", "2025Feb", "2025Mar"]
    for col in month_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    data["q1_2026_oil_import_value"] = data[["2026Jan", "2026Feb", "2026Mar"]].sum(axis=1)
    data["q1_2025_oil_import_value"] = data[["2025Jan", "2025Feb", "2025Mar"]].sum(axis=1)
    total_2026 = data["q1_2026_oil_import_value"].sum()
    out = data[["DataSeries", "q1_2026_oil_import_value", "q1_2025_oil_import_value"]].rename(columns={"DataSeries": "market"})
    out["share_2026_pct"] = out["q1_2026_oil_import_value"] / total_2026 * 100
    out["q1_yoy_pct"] = (out["q1_2026_oil_import_value"] / out["q1_2025_oil_import_value"] - 1) * 100
    return out.sort_values("q1_2026_oil_import_value", ascending=False)


def parse_portwatch_sheet(sheet_name: str) -> pd.DataFrame:
    workbook = RAW / "fetchseries_port_calls_by_country_fsr.xlsx"
    data = pd.read_excel(workbook, sheet_name=sheet_name, engine="openpyxl")
    country_row = data.iloc[0].tolist()
    body = data.iloc[1:].copy()
    out = pd.DataFrame({"date": pd.to_datetime(body.iloc[:, 0], errors="coerce")})
    for country in ["World", "Singapore", "Malaysia", "Indonesia", "China", "Japan", "Korea"]:
        idx = [i for i, value in enumerate(country_row) if str(value) == country]
        if idx:
            out[country] = pd.to_numeric(body[data.columns[idx[0]]], errors="coerce")
    return out.dropna(subset=["date"])


def regional_port_call_windows() -> pd.DataFrame:
    rows = []
    windows = [
        ("pre_war", "2026-01-01", "2026-02-27"),
        ("shock", "2026-02-28", "2026-03-31"),
        ("prolonged", "2026-04-01", "2026-05-01"),
    ]
    for ship_group in ["All cargo vessels", "Container ships", "Tankers"]:
        data = parse_portwatch_sheet(ship_group)
        pre = data[(data["date"] >= "2026-01-01") & (data["date"] <= "2026-02-27")]
        pre_avgs = pre.mean(numeric_only=True)
        for window, start, end in windows:
            sample = data[(data["date"] >= start) & (data["date"] <= end)]
            avgs = sample.mean(numeric_only=True)
            for country, avg_value in avgs.items():
                rows.append(
                    {
                        "ship_group": ship_group,
                        "country": country,
                        "window": window,
                        "start": start,
                        "end": end,
                        "avg_calls_per_day": avg_value,
                        "change_vs_pre_war_pct": (avg_value / pre_avgs[country] - 1) * 100,
                    }
                )
    return pd.DataFrame(rows)


def write_report(
    brent: pd.DataFrame,
    official: pd.DataFrame,
    bunker: pd.DataFrame,
    oil_imports: pd.DataFrame,
    regional: pd.DataFrame,
) -> None:
    brent_idx = brent.set_index("window")
    official_idx = official.set_index("metric")
    top_bunker = bunker.head(8)
    top_oil = oil_imports.head(8)

    def regional_value(ship_group: str, country: str, window: str) -> float:
        row = regional[(regional["ship_group"] == ship_group) & (regional["country"] == country) & (regional["window"] == window)]
        return row["change_vs_pre_war_pct"].iloc[0]

    lines = [
        "# 2026 美伊/美以-伊朗战争对新加坡海运能源数据的初步影响",
        "",
        "## 事件窗口",
        "",
        "- 冲击起点：2026-02-28，美以对伊朗发动打击，随后霍尔木兹海峡航运受阻。",
        "- 短期冲击窗口：2026-02-28 至 2026-03-31。",
        "- 持续扰动窗口：2026-04-01 至 2026-05-01。本地官方新加坡港口数据只到 2026-03，因此 4 月以后主要用 Brent 和 FetchSeries/PortWatch 日度港口数据观察。",
        "",
        "## 价格影响最明显",
        "",
        (
            f"Brent 在 2026-01-01 至 2026-02-27 的战前均价为 {fmt(brent_idx.loc['2026_pre_war', 'avg_brent_price_usd'], 2)} 美元/桶；"
            f"2026-02-28 至 2026-03-31 均价升至 {fmt(brent_idx.loc['shock_2026-02-28_to_2026-03-31', 'avg_brent_price_usd'], 2)}，"
            f"较战前高 {pct(brent_idx.loc['shock_2026-02-28_to_2026-03-31', 'avg_change_vs_pre_war_pct'])}。"
        ),
        (
            f"2026-04-01 至 2026-05-01 均价进一步升至 {fmt(brent_idx.loc['prolonged_2026-04-01_to_2026-05-01', 'avg_brent_price_usd'], 2)}，"
            f"较战前高 {pct(brent_idx.loc['prolonged_2026-04-01_to_2026-05-01', 'avg_change_vs_pre_war_pct'])}；"
            f"本地数据中的最高日价为 {fmt(brent['max_brent_price_usd'].max(), 2)} 美元/桶。"
        ),
        "",
        "## 新加坡港口实体量到 3 月还没有转弱",
        "",
        (
            f"2026 年一季度，货物吞吐量同比 {pct(official_idx.loc['cargo_throughput', 'q1_yoy_pct'])}，"
            f"集装箱吞吐量同比 {pct(official_idx.loc['container_throughput', 'q1_yoy_pct'])}，"
            f"船用燃料销售同比 {pct(official_idx.loc['bunker_sales', 'q1_yoy_pct'])}。"
        ),
        (
            f"油轮到港次数一季度同比 {pct(official_idx.loc['tanker_arrivals_number', 'q1_yoy_pct'])}，"
            f"油轮总吨位同比 {pct(official_idx.loc['tanker_arrivals_gt', 'q1_yoy_pct'])}。"
            "这说明截至 2026 年 3 月，官方月度口径看到的是价格冲击先到，实体吞吐量尚未出现同步下滑。"
        ),
        (
            f"单看 2026 年 3 月，船用燃料销售同比 {pct(official_idx.loc['bunker_sales', 'mar_yoy_pct'])}，"
            f"比 2 月环比 {pct(official_idx.loc['bunker_sales', 'mar_vs_feb_2026_pct'])}；"
            f"油轮到港次数同比 {pct(official_idx.loc['tanker_arrivals_number', 'mar_yoy_pct'])}。"
        ),
        "",
        "## 燃料结构：传统和低硫燃料都被拉动，LNG 继续增长",
        "",
        "2026 年一季度船用燃料销售前几类为：",
    ]
    for row in top_bunker.itertuples():
        lines.append(
            f"- {row.bunker_type}: {fmt(row.q1_2026_bunker_sales, 2)}，份额 {pct(row.share_2026_pct)}，同比 {pct(row.q1_yoy_pct)}"
        )
    lines.extend(
        [
            "",
            "## 油品进口：一季度总额下降，但来源没有重新高度集中",
            "",
            f"2026 年一季度油品进口总额同比 {pct((oil_imports['q1_2026_oil_import_value'].sum() / oil_imports['q1_2025_oil_import_value'].sum() - 1) * 100)}。",
            "Top 来源为：",
        ]
    )
    for row in top_oil.itertuples():
        lines.append(
            f"- {row.market}: 份额 {pct(row.share_2026_pct)}，同比 {pct(row.q1_yoy_pct)}"
        )
    lines.extend(
        [
            "",
            "## 区域日度到港：新加坡没有断崖式下降，但 4 月开始偏弱",
            "",
            (
                "FetchSeries/PortWatch 日度到港口径显示，冲击窗口内新加坡全部货船日均到港较战前 "
                f"{pct(regional_value('All cargo vessels', 'Singapore', 'shock'))}，油轮较战前 "
                f"{pct(regional_value('Tankers', 'Singapore', 'shock'))}。"
            ),
            (
                "到 4 月-5 月 1 日，偏弱更明显：新加坡全部货船日均到港较战前 "
                f"{pct(regional_value('All cargo vessels', 'Singapore', 'prolonged'))}，油轮较战前 "
                f"{pct(regional_value('Tankers', 'Singapore', 'prolonged'))}。"
            ),
            (
                "这和价格冲击的时间差一致：市场价格立刻反应，港口实体量先被库存、合同、替代航线和排队行为缓冲，"
                "更大的影响可能出现在 4 月以后，但官方新加坡港口月度数据目前还没有覆盖。"
            ),
            "",
            "## 判断",
            "",
            "1. 目前可验证的最大影响是油价和燃料成本冲击，不是 3 月新加坡港口吞吐量立刻下滑。",
            "2. 新加坡作为全球最大船用燃料补给枢纽，短期可能受益于抢补给、替代补给和风险库存，但持续封锁会推高燃料成本并压低日度到港。",
            "3. 如果霍尔木兹关闭持续，后续最该跟踪 2026 年 4-6 月的船用燃料销售、油轮到港、低硫燃料/LNG/生物混合燃料份额、以及油品进口来源是否进一步转向非海湾来源。",
        ]
    )
    (OUT / "us_iran_war_impact.md").write_text("\n".join(lines) + "\n" + "\n\n## Interpretation note (October 2026 audit)\n\nEvent-window contrasts and quarterly averages are descriptive, without counterfactual identification; Q1 includes pre-event months. See METHODOLOGY.md.\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    brent = brent_event_windows()
    official = official_q1_impact()
    bunker = bunker_q1_mix()
    oil_imports = oil_imports_q1()
    regional = regional_port_call_windows()

    brent.to_csv(OUT / "us_iran_brent_event_windows.csv", index=False, encoding="utf-8-sig")
    official.to_csv(OUT / "us_iran_official_q1_impact.csv", index=False, encoding="utf-8-sig")
    bunker.to_csv(OUT / "us_iran_bunker_q1_mix.csv", index=False, encoding="utf-8-sig")
    oil_imports.to_csv(OUT / "us_iran_oil_imports_q1.csv", index=False, encoding="utf-8-sig")
    regional.to_csv(OUT / "us_iran_regional_port_call_windows.csv", index=False, encoding="utf-8-sig")
    write_report(brent, official, bunker, oil_imports, regional)
    print((OUT / "us_iran_war_impact.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
