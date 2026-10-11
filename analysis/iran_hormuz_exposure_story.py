from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "malacca_strait_data_package" / "malacca_strait_data_package"
OFFICIAL = PACKAGE / "data" / "official_data_gov_sg"
OUT = ROOT / "analysis" / "output"


CORE_HORMUZ = {"Iran (Islamic Republic Of)", "Kuwait", "Qatar", "Bahrain"}
GULF_WITH_BYPASS = {"Saudi Arabia", "United Arab Emirates"}
NEAR_GULF = {"Oman", "Yemen"}
REGIONAL_BUFFER = {"Malaysia", "Indonesia", "Brunei Darussalam", "Australia"}
ASIAN_REFINERY_TRADE = {"Republic Of Korea", "Mainland China", "India", "Japan", "Taiwan", "Thailand"}
AMERICAS = {
    "United States Of America",
    "Brazil",
    "Mexico",
    "Venezuela",
    "Canada",
    "Argentina",
    "Colombia",
    "Ecuador",
    "Peru",
    "Chile",
}


def fmt(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:,.{digits}f}"


def pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:.{digits}f}%"


def classify_market(market: str) -> str:
    # 分组目标是刻画“霍尔木兹通道暴露”，不是判断贸易伙伴政治属性。
    if market == "Iran (Islamic Republic Of)":
        return "direct_iran"
    if market in CORE_HORMUZ:
        return "hormuz_core_no_large_bypass"
    if market in GULF_WITH_BYPASS:
        return "gulf_with_bypass_capacity"
    if market in NEAR_GULF:
        return "near_gulf_not_core"
    if market in REGIONAL_BUFFER:
        return "regional_se_asia_oceania"
    if market in ASIAN_REFINERY_TRADE:
        return "asian_refinery_trade"
    if market in AMERICAS:
        return "americas"
    return "other"


def load_oil_imports_long() -> pd.DataFrame:
    data = pd.read_csv(OFFICIAL / "merchandise_imports_oil_by_market_monthly.csv", encoding="utf-8")
    long = data.melt(id_vars="DataSeries", var_name="month_raw", value_name="oil_import_value")
    long = long.rename(columns={"DataSeries": "market"})
    long["month_dt"] = pd.to_datetime(long["month_raw"], format="%Y%b", errors="coerce")
    long = long.dropna(subset=["month_dt"]).copy()
    long["month"] = long["month_dt"].dt.to_period("M").astype(str)
    long["year"] = long["month_dt"].dt.year
    long["quarter"] = long["month_dt"].dt.quarter
    long["oil_import_value"] = pd.to_numeric(long["oil_import_value"], errors="coerce").fillna(0)
    long["risk_group"] = long["market"].map(classify_market)
    return long


def add_rollups(table: pd.DataFrame) -> pd.DataFrame:
    for col in [
        "direct_iran",
        "hormuz_core_no_large_bypass",
        "gulf_with_bypass_capacity",
        "near_gulf_not_core",
        "regional_se_asia_oceania",
        "asian_refinery_trade",
        "americas",
        "other",
    ]:
        if col not in table.columns:
            table[col] = 0.0
    table["gulf_total_ex_oman_yemen"] = table["hormuz_core_no_large_bypass"] + table["gulf_with_bypass_capacity"]
    table["gulf_plus_near"] = table["gulf_total_ex_oman_yemen"] + table["near_gulf_not_core"]
    table["non_gulf_substitutes"] = (
        table["regional_se_asia_oceania"] + table["asian_refinery_trade"] + table["americas"]
    )
    return table


def annual_exposure(long: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = long.groupby(["year", "risk_group"])["oil_import_value"].sum().unstack(fill_value=0)
    values = add_rollups(values)
    values["total_oil_import_value"] = long.groupby("year")["oil_import_value"].sum()
    shares = values.div(values["total_oil_import_value"], axis=0) * 100
    shares["total_oil_import_value"] = values["total_oil_import_value"]
    return values.reset_index(), shares.reset_index()


def q1_exposure(long: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    q1 = long[(long["year"].isin([2025, 2026])) & (long["quarter"] == 1)]
    values = q1.groupby(["year", "risk_group"])["oil_import_value"].sum().unstack(fill_value=0)
    values = add_rollups(values)
    values["total_oil_import_value"] = q1.groupby("year")["oil_import_value"].sum()
    shares = values.div(values["total_oil_import_value"], axis=0) * 100
    shares["total_oil_import_value"] = values["total_oil_import_value"]
    yoy = (values.loc[2026] / values.loc[2025] - 1) * 100
    yoy = yoy.replace([np.inf, -np.inf], np.nan).to_frame("q1_2026_yoy_pct")
    return values.reset_index(), shares.reset_index(), yoy.reset_index(names="risk_group")


def recent_monthly_exposure(long: pd.DataFrame) -> pd.DataFrame:
    recent = long[(long["month_dt"] >= "2025-01-01") & (long["month_dt"] <= "2026-03-01")]
    values = recent.groupby(["month", "risk_group"])["oil_import_value"].sum().unstack(fill_value=0)
    values = add_rollups(values)
    values["total_oil_import_value"] = recent.groupby("month")["oil_import_value"].sum()
    shares = values.div(values["total_oil_import_value"], axis=0) * 100
    shares["total_oil_import_value"] = values["total_oil_import_value"]
    return shares.reset_index()


def gulf_market_detail(long: pd.DataFrame) -> pd.DataFrame:
    gulf = long[long["market"].isin(CORE_HORMUZ | GULF_WITH_BYPASS | NEAR_GULF)]
    annual_market = gulf.groupby(["year", "market"], as_index=False)["oil_import_value"].sum()
    total = long.groupby("year", as_index=False).agg(total_oil_import_value=("oil_import_value", "sum"))
    annual_market = annual_market.merge(total, on="year", how="left")
    annual_market["share_pct"] = annual_market["oil_import_value"] / annual_market["total_oil_import_value"] * 100
    annual_market["risk_group"] = annual_market["market"].map(classify_market)
    return annual_market.sort_values(["year", "share_pct"], ascending=[True, False])


def write_report(
    annual_values: pd.DataFrame,
    annual_shares: pd.DataFrame,
    q1_values: pd.DataFrame,
    q1_shares: pd.DataFrame,
    q1_yoy: pd.DataFrame,
    recent_monthly: pd.DataFrame,
    gulf_detail: pd.DataFrame,
) -> None:
    annual = annual_shares.set_index("year")
    q1s = q1_shares.set_index("year")
    q1y = q1_yoy.set_index("risk_group")
    recent = recent_monthly.set_index("month")

    direct_iran_values = annual_values.set_index("year")["direct_iran"]
    iran_nonzero = direct_iran_values[direct_iran_values > 0]
    iran_peak_year = int((annual["direct_iran"]).idxmax())
    iran_peak_share = annual.loc[iran_peak_year, "direct_iran"]

    def gulf_line(year: int) -> str:
        sub = gulf_detail[gulf_detail["year"] == year].sort_values("share_pct", ascending=False)
        return "、".join([f"{row.market} {pct(row.share_pct)}" for row in sub.head(6).itertuples()])

    lines = [
        "# 伊朗不是供应商，而是门口的开关：新加坡油品进口的霍尔木兹暴露",
        "",
        "## 新故事",
        "",
        (
            "前面的分析把重点放在战争如何冲击油价和港口到港。换一个角度看，伊朗对新加坡的影响并不主要来自"
            "“新加坡买了多少伊朗油”，而是来自“海湾油品能不能顺利离开霍尔木兹”。"
        ),
        (
            "在这套数据里，伊朗直接份额长期很小，2011 年峰值也只有 "
            f"{pct(iran_peak_share)}，2019 年后基本消失；但海湾来源仍在新加坡油品进口中占重要位置。"
            "所以这不是一个直接贸易暴露故事，而是一个通道风险和替代来源韧性的故事。"
        ),
        "",
        "## 分组口径",
        "",
        "- `direct_iran`：Iran (Islamic Republic Of)。",
        "- `hormuz_core_no_large_bypass`：Kuwait、Qatar、Bahrain；direct_iran 另行单列。这些来源更能代表海峡核心通道风险。",
        "- `gulf_with_bypass_capacity`：Saudi Arabia、United Arab Emirates。EIA 指出 Saudi 和 UAE 有可绕开霍尔木兹的管道，但可用绕行能力有限。",
        "- `regional_se_asia_oceania`：Malaysia、Indonesia、Brunei、Australia，代表区域/近邻缓冲。",
        "- `asian_refinery_trade`：Korea、Mainland China、India、Japan、Taiwan、Thailand，代表亚洲炼化贸易网络。",
        "- `americas`：United States、Brazil 等远端替代来源。",
        "",
        "## 证据 1：直接伊朗进口不是主风险",
        "",
        (
            f"数据中 direct_iran 的非零年份主要集中在 {int(iran_nonzero.index.min())}-{int(iran_nonzero.index.max())}，"
            f"峰值是 {iran_peak_year} 年的 {pct(iran_peak_share)}。"
            "2019 年以后 direct_iran 基本为 0，2025 年和 2026Q1 也都是 0。"
        ),
        (
            "这意味着，如果只盯着“新加坡是否直接进口伊朗油”，会低估伊朗冲突的真实影响。"
            "真正的风险在于伊朗控制/威胁的霍尔木兹通道影响到其他海湾来源。"
        ),
        "",
        "## 证据 2：新加坡从高度海湾依赖转向多元化，但没有脱离海湾",
        "",
        (
            f"1995 年，新加坡油品进口中 gulf_total_ex_oman_yemen 占 {pct(annual.loc[1995, 'gulf_total_ex_oman_yemen'])}，"
            f"其中 Saudi Arabia、UAE、Kuwait、Qatar 是主要来源。到 2025 年，这个比例降至 "
            f"{pct(annual.loc[2025, 'gulf_total_ex_oman_yemen'])}。"
        ),
        (
            f"同一时期，non_gulf_substitutes 从 {pct(annual.loc[1995, 'non_gulf_substitutes'])} 升至 "
            f"{pct(annual.loc[2025, 'non_gulf_substitutes'])}。这说明新加坡确实在用东南亚、东北亚、美洲等来源分散供应风险。"
        ),
        "1995 年海湾来源细分：" + gulf_line(1995),
        "2025 年海湾来源细分：" + gulf_line(2025),
        "",
        "## 证据 3：2026Q1 海湾来源金额占比上升，但变化主要出现在冲突前",
        "",
        (
            f"2025Q1 海湾来源占比为 {pct(q1s.loc[2025, 'gulf_total_ex_oman_yemen'])}，"
            f"2026Q1 升至 {pct(q1s.loc[2026, 'gulf_total_ex_oman_yemen'])}；"
            f"Saudi/UAE 组从 {pct(q1s.loc[2025, 'gulf_with_bypass_capacity'])} "
            f"升至 {pct(q1s.loc[2026, 'gulf_with_bypass_capacity'])}。"
        ),
        (
            "但月度数据表明，这种季度变化不能直接归因于 2026 年 2 月 28 日的冲突："
            f"2026 年 1 月海湾占比已经为 {pct(recent.loc['2026-01', 'gulf_total_ex_oman_yemen'])}，"
            f"2 月为 {pct(recent.loc['2026-02', 'gulf_total_ex_oman_yemen'])}，"
            f"3 月回落到 {pct(recent.loc['2026-03', 'gulf_total_ex_oman_yemen'])}。"
        ),
        (
            f"同期 2026Q1 油品进口总金额同比变化为 "
            f"{pct((q1_values.set_index('year').loc[2026, 'total_oil_import_value'] / q1_values.set_index('year').loc[2025, 'total_oil_import_value'] - 1) * 100)}。"
            "数据反映来源金额结构变化；还不能分辨价格、数量与采购时点的贡献。"
        ),
        "",
        "## 证据 4：2025 年夏季海湾来源占比走高",
        "",
        (
            f"2025 年 6 月，也就是十二日战争发生月，gulf_total_ex_oman_yemen 月度份额升至 "
            f"{pct(recent.loc['2025-06', 'gulf_total_ex_oman_yemen'])}；7 月仍为 "
            f"{pct(recent.loc['2025-07', 'gulf_total_ex_oman_yemen'])}。"
        ),
        (
            f"相比之下，2025 年 1-3 月该比例只有 {pct(q1s.loc[2025, 'gulf_total_ex_oman_yemen'])}。"
            "月度份额存在变化，但缺少对照期和价格数量分解，无法将其归因于冲突或库存行为。"
        ),
        "",
        "## 这条新故事怎么讲",
        "",
        "可以把题目改成：**伊朗不是新加坡油品供应商，而是海湾供应链的风险开关**。",
        "",
        "故事结构：",
        "",
        "1. 直接暴露很小：伊朗在新加坡油品进口中的直接份额几乎已经消失。",
        "2. 间接暴露仍大：Saudi、UAE、Qatar、Kuwait 等海湾来源合计仍占 2025 年约三分之一、2026Q1 接近四成。",
        "3. 多元化确实存在：非海湾替代来源长期抬升，说明新加坡不是被单一供应国锁定。",
        "4. 海湾风险仍值得关注：长期来源多元化并未消除海湾来源占比；现有数据尚未识别战时转向。",
        "5. 研究假说是通道风险可能通过采购来源、燃料价格与船舶补给传导；需要进一步数据验证传导机制。",
        "",
        "## 外部事实支撑",
        "",
        "- EIA 2025 年 6 月文章指出，2024 年通过霍尔木兹的油流约为 2,000 万桶/日，约占全球石油液体消费五分之一；霍尔木兹还承载约五分之一全球 LNG 贸易，主要来自 Qatar。",
        "- EIA 同文指出 Saudi Arabia 和 UAE 有绕行霍尔木兹的管道，但可用绕行能力有限；2024 年有 84% 的霍尔木兹原油和凝析油、83% 的 LNG 流向亚洲市场。",
        "",
        "来源：https://www.eia.gov/todayinenergy/detail.php?id=65504+",
        "",
        "## 输出表",
        "",
        "- `analysis/output/iran_hormuz_exposure_annual_values.csv`",
        "- `analysis/output/iran_hormuz_exposure_annual_shares.csv`",
        "- `analysis/output/iran_hormuz_exposure_q1_values.csv`",
        "- `analysis/output/iran_hormuz_exposure_q1_shares.csv`",
        "- `analysis/output/iran_hormuz_exposure_q1_yoy.csv`",
        "- `analysis/output/iran_hormuz_exposure_recent_monthly.csv`",
        "- `analysis/output/iran_hormuz_gulf_market_detail.csv`",
    ]
    (OUT / "iran_hormuz_exposure_story.md").write_text("\n".join(lines) + "\n" + "\n\n## Interpretation note (October 2026 audit)\n\nQ1 values include pre-event months; import-value composition changes do not identify war effects. Trade-partner groups do not measure actual Hormuz transit. See METHODOLOGY.md.\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    long = load_oil_imports_long()
    annual_values, annual_shares = annual_exposure(long)
    q1_values, q1_shares, q1_yoy = q1_exposure(long)
    recent_monthly = recent_monthly_exposure(long)
    gulf_detail = gulf_market_detail(long)

    long.to_csv(OUT / "iran_hormuz_oil_imports_long_classified.csv", index=False, encoding="utf-8-sig")
    annual_values.to_csv(OUT / "iran_hormuz_exposure_annual_values.csv", index=False, encoding="utf-8-sig")
    annual_shares.to_csv(OUT / "iran_hormuz_exposure_annual_shares.csv", index=False, encoding="utf-8-sig")
    q1_values.to_csv(OUT / "iran_hormuz_exposure_q1_values.csv", index=False, encoding="utf-8-sig")
    q1_shares.to_csv(OUT / "iran_hormuz_exposure_q1_shares.csv", index=False, encoding="utf-8-sig")
    q1_yoy.to_csv(OUT / "iran_hormuz_exposure_q1_yoy.csv", index=False, encoding="utf-8-sig")
    recent_monthly.to_csv(OUT / "iran_hormuz_exposure_recent_monthly.csv", index=False, encoding="utf-8-sig")
    gulf_detail.to_csv(OUT / "iran_hormuz_gulf_market_detail.csv", index=False, encoding="utf-8-sig")
    write_report(annual_values, annual_shares, q1_values, q1_shares, q1_yoy, recent_monthly, gulf_detail)
    print((OUT / "iran_hormuz_exposure_story.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
