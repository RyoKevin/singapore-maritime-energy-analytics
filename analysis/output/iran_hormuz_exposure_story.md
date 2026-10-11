# 伊朗不是供应商，而是门口的开关：新加坡油品进口的霍尔木兹暴露

## 新故事

前面的分析把重点放在战争如何冲击油价和港口到港。换一个角度看，伊朗对新加坡的影响并不主要来自“新加坡买了多少伊朗油”，而是来自“海湾油品能不能顺利离开霍尔木兹”。
在这套数据里，伊朗直接份额长期很小，2011 年峰值也只有 4.4%，2019 年后基本消失；但海湾来源仍在新加坡油品进口中占重要位置。所以这不是一个直接贸易暴露故事，而是一个通道风险和替代来源韧性的故事。

## 分组口径

- `direct_iran`：Iran (Islamic Republic Of)。
- `hormuz_core_no_large_bypass`：Kuwait、Qatar、Bahrain；direct_iran 另行单列。这些来源更能代表海峡核心通道风险。
- `gulf_with_bypass_capacity`：Saudi Arabia、United Arab Emirates。EIA 指出 Saudi 和 UAE 有可绕开霍尔木兹的管道，但可用绕行能力有限。
- `regional_se_asia_oceania`：Malaysia、Indonesia、Brunei、Australia，代表区域/近邻缓冲。
- `asian_refinery_trade`：Korea、Mainland China、India、Japan、Taiwan、Thailand，代表亚洲炼化贸易网络。
- `americas`：United States、Brazil 等远端替代来源。

## 证据 1：直接伊朗进口不是主风险

数据中 direct_iran 的非零年份主要集中在 2007-2019，峰值是 2011 年的 4.4%。2019 年以后 direct_iran 基本为 0，2025 年和 2026Q1 也都是 0。
这意味着，如果只盯着“新加坡是否直接进口伊朗油”，会低估伊朗冲突的真实影响。真正的风险在于伊朗控制/威胁的霍尔木兹通道影响到其他海湾来源。

## 证据 2：新加坡从高度海湾依赖转向多元化，但没有脱离海湾

1995 年，新加坡油品进口中 gulf_total_ex_oman_yemen 占 68.6%，其中 Saudi Arabia、UAE、Kuwait、Qatar 是主要来源。到 2025 年，这个比例降至 36.0%。
同一时期，non_gulf_substitutes 从 22.6% 升至 59.2%。这说明新加坡确实在用东南亚、东北亚、美洲等来源分散供应风险。
1995 年海湾来源细分：Saudi Arabia 37.7%、United Arab Emirates 14.3%、Kuwait 12.7%、Qatar 3.2%、Oman 2.3%、Yemen 1.6%
2025 年海湾来源细分：United Arab Emirates 19.9%、Qatar 7.9%、Saudi Arabia 5.7%、Kuwait 1.8%、Oman 1.3%、Bahrain 0.7%

## 证据 3：2026Q1 反而出现“海湾回流”，暴露度短期上升

2025Q1 gulf_total_ex_oman_yemen 份额为 29.6%，2026Q1 升至 38.8%。其中 gulf_with_bypass_capacity 从 19.9% 升至 29.9%，同比金额增长 37.9%。
这背后主要是 UAE 和 Saudi Arabia 的份额上升。相反，Americas 组金额同比 -69.3%，asian_refinery_trade 同比 -16.2%。
所以 2026Q1 的故事不是“新加坡立即摆脱海湾”，而是“总进口额下降 -8.1%，但海湾中带有绕行能力的供应者权重上升”。这是一种战时供应再配置，而不是单纯需求下滑。

## 证据 4：十二日战争期间也能看到通道风险的提前反应

2025 年 6 月，也就是十二日战争发生月，gulf_total_ex_oman_yemen 月度份额升至 42.2%；7 月仍为 42.1%。
相比之下，2025 年 1-3 月该比例只有 29.6%。这说明短期军事冲突不一定马上压低新加坡港口活动，但可能先改变油品采购来源和库存行为。

## 这条新故事怎么讲

可以把题目改成：**伊朗不是新加坡油品供应商，而是海湾供应链的风险开关**。

故事结构：

1. 直接暴露很小：伊朗在新加坡油品进口中的直接份额几乎已经消失。
2. 间接暴露仍大：Saudi、UAE、Qatar、Kuwait 等海湾来源合计仍占 2025 年约三分之一、2026Q1 接近四成。
3. 多元化确实存在：非海湾替代来源长期抬升，说明新加坡不是被单一供应国锁定。
4. 但多元化不等于免疫：当霍尔木兹被扰动时，有绕行能力的海湾供应者权重反而上升，说明市场会转向“更可靠的海湾出口节点”，而不是完全离开海湾。
5. 因此，新加坡的角色是风险再分配枢纽：它把海湾冲击转化为油品来源再配置、燃料成本上升和船舶补给行为变化。

## 外部事实支撑

- EIA 2025 年 6 月文章指出，2024 年通过霍尔木兹的油流约为 2,000 万桶/日，约占全球石油液体消费五分之一；霍尔木兹还承载约五分之一全球 LNG 贸易，主要来自 Qatar。
- EIA 同文指出 Saudi Arabia 和 UAE 有绕行霍尔木兹的管道，但可用绕行能力有限；2024 年有 84% 的霍尔木兹原油和凝析油、83% 的 LNG 流向亚洲市场。

来源：https://www.eia.gov/todayinenergy/detail.php?id=65504+

## 输出表

- `analysis/output/iran_hormuz_exposure_annual_values.csv`
- `analysis/output/iran_hormuz_exposure_annual_shares.csv`
- `analysis/output/iran_hormuz_exposure_q1_values.csv`
- `analysis/output/iran_hormuz_exposure_q1_shares.csv`
- `analysis/output/iran_hormuz_exposure_q1_yoy.csv`
- `analysis/output/iran_hormuz_exposure_recent_monthly.csv`
- `analysis/output/iran_hormuz_gulf_market_detail.csv`


## Interpretation note (October 2026 audit)

The 2026Q1 year-over-year changes above are **descriptive import-value composition statistics**, including January and most of February before the February 28 conflict. They cannot establish that the crisis caused the observed rise in Saudi/UAE shares. Value shares can also change as prices change. The June–July 2025 differences likewise do not identify a conflict effect without comparable pre-trend and control-period checks. The country-based Gulf proxy does not measure actual vessel passage through Hormuz. See [METHODOLOGY.md](../../../METHODOLOGY.md).
