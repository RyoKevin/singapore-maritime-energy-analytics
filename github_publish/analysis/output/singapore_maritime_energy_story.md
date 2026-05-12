# 新加坡海运能源枢纽：从“吞吐量增长”到“高吨位与燃料服务”

## 一句话结论

1995-2025 年，新加坡港的核心变化不是船舶到港次数暴涨，而是服务对象变得更大、能源补给更集中、燃料和油品来源结构更复杂。货物吞吐量约翻一倍，集装箱吞吐量和船用燃料销售约增长三倍，但船舶到港次数只增长约五分之一；与此同时，靠港船舶总吨位增长近五倍。这说明新加坡的枢纽价值更多来自大船、高频补给、能源中转和燃料供应能力，而不是简单的“船更多”。

## 数据与清洗口径

- 主数据使用 `data/official_data_gov_sg/` 下的官方月度 CSV：货物吞吐量、集装箱吞吐量、船舶到港、油轮到港、船用燃料销售和油品进口市场。
- Brent 油价使用 `raw/fred_brent_crude_oil.csv`，由日度均值聚合到月度。
- `merchandise_imports_oil_by_market_monthly.csv` 是市场为行、月份为列的宽表，已清洗成长表并计算年度市场份额、Top 5 份额和 HHI 集中度。
- `fetchseries_port_calls_by_country_fsr.xlsx` 仅用作区域背景对照，主结论仍以官方新加坡月度数据为准。
- 2026 年官方港口数据只到 3 月，FRED 油价到 5 月，因此年度同比和峰值判断只使用 2025 年及之前的完整年份。

## 证据 1：规模扩张主要来自大船化，而不是到港次数

1995 到 2025 年，货物吞吐量从 305,484.0 增至 614,352.2，增长 101.1%，年化约 2.4%。集装箱吞吐量从 11,846.0 增至 44,663.7，增长 277.0%，年化约 4.5%。
同一时期，船舶到港次数只从 163,507 增至 199,221，增长 21.8%；但到港船舶总吨位从 1,128,104.7 增至 6,605,479.1，增长 485.5%。
因此，每次到港对应的平均总吨位从 6.90 增至 33.16，约为 1995 年的 4.81 倍。2025 年集装箱吞吐量、船用燃料销售和船舶总吨位均达到完整年份样本峰值；货物吞吐量的峰值在 2018 年，2025 年仍为峰值的 97.5%。

## 证据 2：疫情冲击下，燃料补给比普通到港更有韧性

2020 年是结构差异最清楚的一年：总船舶到港次数同比下降 24.6%，货物吞吐量下降 5.7%，但船用燃料销售同比增长 5.0%，油轮到港次数增长 5.2%，油轮总吨位增长 8.9%。
这说明当普通靠港活动受冲击时，新加坡的能源航运服务仍保持强度。2020 年每次到港对应的船用燃料销售从 2019 年的 0.229 升至 0.319，不是因为所有活动都扩张，而是因为留下来的船舶和业务更偏向大吨位、油轮与补给需求。

## 证据 3：燃料结构在 2020 年发生断点，随后替代燃料开始出现

2019 年，Marine Fuel Oil 仍占船用燃料销售的 80.3%，Low Sulphur Fuel Oil 占 11.5%。到 2020 年，Low Sulphur Fuel Oil 跃升到 68.4%，Marine Fuel Oil 降至 21.4%。
到 2025 年，Low Sulphur Fuel Oil 仍为第一大类，占 50.8%；Marine Fuel Oil 回升到 38.2%，说明低硫化不是简单替代全部传统燃油，而是形成多燃料并存。
更小但值得跟踪的是新燃料：Bio-blended 组在 2024 年占 1.6%，2025 年升至 2.4%；LNG 从 2024 年的 0.8% 升至 2025 年的 1.0%。这些份额仍小，但它们显示新加坡港已经不只是卖油量，而是在形成替代燃料供给能力。

## 证据 4：油品进口来源从高度集中转向多中心

1995 年油品进口市场高度集中：Top 5 市场合计占 77.8%，HHI 为 1,935；第一来源是 Saudi Arabia，占 37.7%。
到 2025 年，Top 5 合计降至 52.6%，HHI 降至 861；第一来源变为 United Arab Emirates，占 19.9%。
1995 年 Top 5 来源：Saudi Arabia 37.7%、United Arab Emirates 14.3%、Kuwait 12.7%、Malaysia 10.0%、Qatar 3.2%
2025 年 Top 5 来源：United Arab Emirates 19.9%、Malaysia 10.4%、Republic Of Korea 8.1%、Qatar 7.9%、Indonesia 6.3%

## 区域对照：新加坡更像成熟高服务密度节点

FetchSeries/PortWatch 的日度港口到港数据给出一个背景：2019-2025 年，新加坡全部货船到港指数从 100 升至 103.0，马来西亚升至 136.4，印尼升至 127.5；油轮到港指数中新加坡为 108.3，马来西亚为 203.1，印尼为 134.1。
这意味着区域内新增到港增长并不全部集中在新加坡；新加坡的优势更像成熟枢纽：到港增长温和，但总吨位、燃料销售和多燃料服务能力更强。

## 故事判断

这组数据支持一个合理的数据故事：

1. 新加坡港的长期增长不是靠单纯增加船数，而是靠更大船舶、更高总吨位和更强补给服务。
2. 能源航运业务在冲击期更有韧性，2020 年普通到港明显下降，但油轮和燃料销售仍上升。
3. 2020 年以后，燃料结构从传统 Marine Fuel Oil 主导转向低硫燃料主导，近年开始出现生物混合燃料、LNG、甲醇等小份额新燃料。
4. 油品进口来源从 1990 年代中东高度集中，转向 2020 年代的中东、东南亚、东北亚、美洲等多中心结构。

因此，如果要把这个项目讲成论文或简历项目，题目可以是：**新加坡海运能源枢纽的结构升级：大船化、燃料转型与进口来源多元化**。

## 输出文件

- 清洗后的月度面板：`analysis/output/monthly_panel.csv`
- 年度关键指标：`analysis/output/annual_key_metrics.csv`
- 船用燃料结构：`analysis/output/bunker_mix_annual.csv` 与 `analysis/output/bunker_mix_grouped_annual.csv`
- 油品进口长表与市场份额：`analysis/output/oil_imports_long.csv`、`analysis/output/oil_import_market_shares_annual.csv`、`analysis/output/oil_import_concentration_annual.csv`
- 区域港口到港对照：`analysis/output/regional_port_calls_annual.csv`
- 图表：`analysis/charts/singapore_maritime_index.svg`、`analysis/charts/bunker_fuel_mix_share.svg`、`analysis/charts/oil_import_top_market_shares.svg`、`analysis/charts/regional_port_calls_index.svg`
