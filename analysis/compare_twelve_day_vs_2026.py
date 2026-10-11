from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "malacca_strait_data_package" / "malacca_strait_data_package"
OFFICIAL = PACKAGE / "data" / "official_data_gov_sg"
RAW = PACKAGE / "raw"
OUT = ROOT / "analysis" / "output"


def fmt(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:,.{digits}f}"


def pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}%"


def read_official(name: str) -> pd.DataFrame:
    # 官方 CSV 用 UTF-8 读取。
    return pd.read_csv(OFFICIAL / name, encoding="utf-8")


def brent_windows() -> pd.DataFrame:
    brent = pd.read_csv(RAW / "fred_brent_crude_oil.csv", encoding="utf-8")
    brent["date"] = pd.to_datetime(brent["date"])
    brent["brent_price_usd"] = pd.to_numeric(brent["brent_price_usd"], errors="coerce")
    windows = [
        ("twelve_day_pre", "2025-05-01", "2025-06-12", "十二日战争战前"),
        ("twelve_day_event", "2025-06-13", "2025-06-24", "十二日战争事件期"),
        ("twelve_day_post", "2025-06-25", "2025-07-31", "十二日战争战后一个月"),
        ("war_2026_pre", "2026-01-01", "2026-02-27", "2026 战前"),
        ("war_2026_shock", "2026-02-28", "2026-03-31", "2026 冲击期"),
        ("war_2026_prolonged", "2026-04-01", "2026-05-01", "2026 持续扰动期"),
    ]
    rows = []
    for key, start, end, label in windows:
        sample = brent[(brent["date"] >= start) & (brent["date"] <= end)]
        rows.append(
            {
                "window": key,
                "label": label,
                "start": start,
                "end": end,
                "observations": len(sample),
                "avg_brent_price_usd": sample["brent_price_usd"].mean(),
                "min_brent_price_usd": sample["brent_price_usd"].min(),
                "max_brent_price_usd": sample["brent_price_usd"].max(),
            }
        )
    out = pd.DataFrame(rows)
    pre_12 = out.loc[out["window"] == "twelve_day_pre", "avg_brent_price_usd"].iloc[0]
    pre_26 = out.loc[out["window"] == "war_2026_pre", "avg_brent_price_usd"].iloc[0]
    out["avg_change_vs_own_pre_pct"] = np.where(
        out["window"].str.startswith("twelve"),
        (out["avg_brent_price_usd"] / pre_12 - 1) * 100,
        (out["avg_brent_price_usd"] / pre_26 - 1) * 100,
    )
    out["max_change_vs_own_pre_avg_pct"] = np.where(
        out["window"].str.startswith("twelve"),
        (out["max_brent_price_usd"] / pre_12 - 1) * 100,
        (out["max_brent_price_usd"] / pre_26 - 1) * 100,
    )
    return out


def monthly_2025_metrics() -> pd.DataFrame:
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

        def value(month: str) -> float:
            return data.loc[data["month"] == month, col].iloc[0]

        june_2025 = value("2025-06")
        q2_2025 = data[(data["month_dt"] >= "2025-04-01") & (data["month_dt"] <= "2025-06-01")][col].sum()
        q2_2024 = data[(data["month_dt"] >= "2024-04-01") & (data["month_dt"] <= "2024-06-01")][col].sum()
        q3_2025 = data[(data["month_dt"] >= "2025-07-01") & (data["month_dt"] <= "2025-09-01")][col].sum()
        q3_2024 = data[(data["month_dt"] >= "2024-07-01") & (data["month_dt"] <= "2024-09-01")][col].sum()
        rows.append(
            {
                "metric": metric,
                "june_2025_yoy_pct": (june_2025 / value("2024-06") - 1) * 100,
                "june_2025_vs_may_2025_pct": (june_2025 / value("2025-05") - 1) * 100,
                "july_2025_vs_june_2025_pct": (value("2025-07") / june_2025 - 1) * 100,
                "q2_2025_yoy_pct": (q2_2025 / q2_2024 - 1) * 100,
                "q3_2025_yoy_pct": (q3_2025 / q3_2024 - 1) * 100,
            }
        )
    return pd.DataFrame(rows)


def regional_windows() -> pd.DataFrame:
    workbook = RAW / "fetchseries_port_calls_by_country_fsr.xlsx"
    windows = [
        ("twelve_day_pre", "2025-05-01", "2025-06-12"),
        ("twelve_day_event", "2025-06-13", "2025-06-24"),
        ("twelve_day_post", "2025-06-25", "2025-07-31"),
        ("war_2026_pre", "2026-01-01", "2026-02-27"),
        ("war_2026_shock", "2026-02-28", "2026-03-31"),
        ("war_2026_prolonged", "2026-04-01", "2026-05-01"),
    ]
    rows = []
    for sheet in ["All cargo vessels", "Container ships", "Tankers"]:
        raw = pd.read_excel(workbook, sheet_name=sheet, engine="openpyxl")
        country_row = raw.iloc[0].tolist()
        body = raw.iloc[1:].copy()
        data = pd.DataFrame({"date": pd.to_datetime(body.iloc[:, 0], errors="coerce")})
        for country in ["World", "Singapore", "Malaysia", "Indonesia", "China", "Japan", "Korea"]:
            idx = [i for i, value in enumerate(country_row) if str(value) == country]
            if idx:
                data[country] = pd.to_numeric(body[raw.columns[idx[0]]], errors="coerce")
        data = data.dropna(subset=["date"])
        averages = {}
        for key, start, end in windows:
            averages[key] = data[(data["date"] >= start) & (data["date"] <= end)].mean(numeric_only=True)
        for country in ["World", "Singapore", "Malaysia", "Indonesia", "China", "Japan", "Korea"]:
            rows.append(
                {
                    "ship_group": sheet,
                    "country": country,
                    "twelve_day_event_vs_pre_pct": (averages["twelve_day_event"][country] / averages["twelve_day_pre"][country] - 1) * 100,
                    "twelve_day_post_vs_pre_pct": (averages["twelve_day_post"][country] / averages["twelve_day_pre"][country] - 1) * 100,
                    "war_2026_shock_vs_pre_pct": (averages["war_2026_shock"][country] / averages["war_2026_pre"][country] - 1) * 100,
                    "war_2026_prolonged_vs_pre_pct": (averages["war_2026_prolonged"][country] / averages["war_2026_pre"][country] - 1) * 100,
                }
            )
    return pd.DataFrame(rows)


def write_report(brent: pd.DataFrame, monthly: pd.DataFrame, regional: pd.DataFrame) -> None:
    b = brent.set_index("window")
    m = monthly.set_index("metric")

    def r(ship_group: str, country: str, col: str) -> float:
        return regional[(regional["ship_group"] == ship_group) & (regional["country"] == country)][col].iloc[0]

    lines = [
        "# 十二日战争与 2026 霍尔木兹危机：对新加坡海运能源数据的对比",
        "",
        "## 核心区别",
        "",
        "十二日战争是 2025-06-13 至 2025-06-24 的短促军事冲突，主要表现为油价风险溢价；2026 年冲突从 2026-02-28 开始并演化为霍尔木兹海峡长期通行受阻，主要表现为供应链和燃料成本冲击。",
        "",
        "## 油价：2026 冲击幅度约为十二日战争的 3 到 4 倍",
        "",
        (
            f"十二日战争战前 Brent 均价为 {fmt(b.loc['twelve_day_pre', 'avg_brent_price_usd'], 2)} 美元/桶，"
            f"事件期均价为 {fmt(b.loc['twelve_day_event', 'avg_brent_price_usd'], 2)}，"
            f"较战前高 {pct(b.loc['twelve_day_event', 'avg_change_vs_own_pre_pct'])}；"
            f"事件期最高价较战前均价高 {pct(b.loc['twelve_day_event', 'max_change_vs_own_pre_avg_pct'])}。"
        ),
        (
            f"2026 年冲击期 Brent 均价较战前高 {pct(b.loc['war_2026_shock', 'avg_change_vs_own_pre_pct'])}，"
            f"4 月至 5 月 1 日持续扰动期较战前高 {pct(b.loc['war_2026_prolonged', 'avg_change_vs_own_pre_pct'])}；"
            f"最高价较战前均价高 {pct(b.loc['war_2026_prolonged', 'max_change_vs_own_pre_avg_pct'])}。"
        ),
        "",
        "## 新加坡官方月度数据：十二日战争没有打断港口活动",
        "",
        (
            f"2025 年 6 月，货物吞吐量同比 {pct(m.loc['cargo_throughput', 'june_2025_yoy_pct'])}，"
            f"集装箱吞吐量同比 {pct(m.loc['container_throughput', 'june_2025_yoy_pct'])}，"
            f"船用燃料销售同比 {pct(m.loc['bunker_sales', 'june_2025_yoy_pct'])}。"
        ),
        (
            f"2025 年 6 月油轮到港次数同比 {pct(m.loc['tanker_arrivals_number', 'june_2025_yoy_pct'])}，"
            f"油轮总吨位同比 {pct(m.loc['tanker_arrivals_gt', 'june_2025_yoy_pct'])}。"
            "也就是说，十二日战争期间没有看到新加坡港口实体量同步下滑。"
        ),
        (
            f"战后一个月也没有明显塌陷：2025 年 7 月船用燃料销售比 6 月高 {pct(m.loc['bunker_sales', 'july_2025_vs_june_2025_pct'])}，"
            f"油轮到港次数比 6 月高 {pct(m.loc['tanker_arrivals_number', 'july_2025_vs_june_2025_pct'])}。"
        ),
        "",
        "## 日度港口对照：十二日战争几乎是噪声，2026 才开始压低到港",
        "",
        (
            "FetchSeries/PortWatch 日度口径中，十二日战争事件期新加坡全部货船日均到港较战前 "
            f"{pct(r('All cargo vessels', 'Singapore', 'twelve_day_event_vs_pre_pct'))}，油轮为 "
            f"{pct(r('Tankers', 'Singapore', 'twelve_day_event_vs_pre_pct'))}。"
        ),
        (
            "2026 年冲击期新加坡全部货船日均到港较战前 "
            f"{pct(r('All cargo vessels', 'Singapore', 'war_2026_shock_vs_pre_pct'))}，油轮为 "
            f"{pct(r('Tankers', 'Singapore', 'war_2026_shock_vs_pre_pct'))}；"
            "到 4 月至 5 月 1 日，二者分别为 "
            f"{pct(r('All cargo vessels', 'Singapore', 'war_2026_prolonged_vs_pre_pct'))} 和 "
            f"{pct(r('Tankers', 'Singapore', 'war_2026_prolonged_vs_pre_pct'))}。"
        ),
        "",
        "## 解释",
        "",
        "1. 十二日战争持续时间短，没有造成霍尔木兹海峡长期关闭，更多是风险溢价冲击。",
        "2. 2026 年冲突改变了通行条件、保险成本和燃料供应预期，所以油价上涨更大、持续更久。",
        "3. 新加坡港口作为补给枢纽，在短期战争中可以被库存和抢补给支撑；但通道长期受阻时，日度到港开始偏弱，后续压力更可能体现在 2026 年 4-6 月官方数据。",
        "",
        "## 输出表",
        "",
        "- `analysis/output/twelve_day_vs_2026_brent_windows.csv`",
        "- `analysis/output/twelve_day_2025_monthly_metrics.csv`",
        "- `analysis/output/twelve_day_vs_2026_regional_daily.csv`",
    ]
    (OUT / "twelve_day_vs_2026_comparison.md").write_text("\n".join(lines) + "\n" + "\\n\\n## Interpretation note (October 2026 audit)\\n\\nEvent-window contrasts and quarterly averages are descriptive, without counterfactual identification; Q1 includes pre-event months. See METHODOLOGY.md.\\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    brent = brent_windows()
    monthly = monthly_2025_metrics()
    regional = regional_windows()
    brent.to_csv(OUT / "twelve_day_vs_2026_brent_windows.csv", index=False, encoding="utf-8-sig")
    monthly.to_csv(OUT / "twelve_day_2025_monthly_metrics.csv", index=False, encoding="utf-8-sig")
    regional.to_csv(OUT / "twelve_day_vs_2026_regional_daily.csv", index=False, encoding="utf-8-sig")
    write_report(brent, monthly, regional)
    print((OUT / "twelve_day_vs_2026_comparison.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
