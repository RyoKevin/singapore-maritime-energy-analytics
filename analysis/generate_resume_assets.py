from __future__ import annotations

from html import escape
from pathlib import Path
from shutil import copyfile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "output"
CHARTS = ROOT / "analysis" / "charts"
DOCS = ROOT / "docs"
DOC_ASSETS = DOCS / "assets"

COLORS = [
    "#2454A6",
    "#D95F02",
    "#1B9E77",
    "#7570B3",
    "#E6AB02",
    "#66A61E",
    "#A6761D",
    "#E7298A",
]


def text(x: float, y: float, value: str, size: int = 12, anchor: str = "middle", weight: str = "400") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Microsoft YaHei, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#1f2933">{escape(value)}</text>'
    )


def line_svg(path: Path, title: str, series: list[dict[str, object]], y_label: str) -> None:
    # 生成无依赖 SVG，方便 README 和 GitHub Pages 直接展示。
    width, height = 980, 560
    left, right, top, bottom = 78, 220, 64, 72
    pw, ph = width - left - right, height - top - bottom
    xs = [float(x) for item in series for x in item["x"]]
    ys = [float(y) for item in series for y in item["y"]]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(0, min(ys) * 0.95), max(ys) * 1.08

    def sx(x: float) -> float:
        return left + (x - xmin) / (xmax - xmin) * pw

    def sy(y: float) -> float:
        return top + (ymax - y) / (ymax - ymin) * ph

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(width / 2, 34, title, 20, weight="700"),
        f'<line x1="{left}" y1="{top + ph}" x2="{left + pw}" y2="{top + ph}" stroke="#334155"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + ph}" stroke="#334155"/>',
    ]
    for tick in [ymin + i * (ymax - ymin) / 5 for i in range(6)]:
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        parts.append(text(left - 10, y + 4, f"{tick:.0f}", 11, anchor="end"))

    step = max(1, round((xmax - xmin) / 8))
    ticks = list(range(int(xmin), int(xmax) + 1, step))
    if int(xmax) not in ticks:
        ticks.append(int(xmax))
    for tick in ticks:
        x = sx(float(tick))
        parts.append(f'<line x1="{x:.1f}" y1="{top + ph}" x2="{x:.1f}" y2="{top + ph + 5}" stroke="#334155"/>')
        parts.append(text(x, top + ph + 23, str(tick), 11))
    parts.append(text(28, top + ph / 2, y_label, 12))

    for idx, item in enumerate(series):
        color = COLORS[idx % len(COLORS)]
        points = " ".join(f"{sx(float(x)):.1f},{sy(float(y)):.1f}" for x, y in zip(item["x"], item["y"]))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.6"/>')
        ly = top + 24 + idx * 24
        parts.append(f'<line x1="{left + pw + 26}" y1="{ly}" x2="{left + pw + 52}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
        parts.append(text(left + pw + 60, ly + 4, str(item["name"]), 12, anchor="start"))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def grouped_bar_svg(path: Path, title: str, labels: list[str], groups: list[dict[str, object]], y_label: str) -> None:
    width, height = 980, 560
    left, right, top, bottom = 88, 210, 64, 96
    pw, ph = width - left - right, height - top - bottom
    max_y = max(float(v) for group in groups for v in group["values"]) * 1.15
    bar_group_w = pw / len(labels)
    bar_w = min(36, bar_group_w / (len(groups) + 1.2))

    def sy(v: float) -> float:
        return top + (max_y - v) / max_y * ph

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(width / 2, 34, title, 20, weight="700"),
        f'<line x1="{left}" y1="{top + ph}" x2="{left + pw}" y2="{top + ph}" stroke="#334155"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + ph}" stroke="#334155"/>',
    ]
    for i in range(6):
        tick = max_y * i / 5
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="#e2e8f0"/>')
        parts.append(text(left - 10, y + 4, f"{tick:.0f}", 11, anchor="end"))
    parts.append(text(28, top + ph / 2, y_label, 12))

    for i, label in enumerate(labels):
        gx = left + i * bar_group_w + bar_group_w / 2
        for j, group in enumerate(groups):
            value = float(group["values"][i])
            x = gx - (len(groups) * bar_w) / 2 + j * bar_w
            y = sy(value)
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 4:.1f}" height="{top + ph - y:.1f}" '
                f'fill="{COLORS[j % len(COLORS)]}"/>'
            )
        parts.append(text(gx, top + ph + 24, label, 11))
    for j, group in enumerate(groups):
        ly = top + 24 + j * 24
        parts.append(f'<rect x="{left + pw + 26}" y="{ly - 11}" width="16" height="16" fill="{COLORS[j % len(COLORS)]}"/>')
        parts.append(text(left + pw + 50, ly + 3, str(group["name"]), 12, anchor="start"))
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def make_brent_event_chart() -> None:
    data = pd.read_csv(OUT / "twelve_day_vs_2026_brent_windows.csv", encoding="utf-8-sig")
    labels = ["战前", "事件/冲击", "战后/持续"]
    twelve = data[data["window"].str.startswith("twelve")]["avg_change_vs_own_pre_pct"].tolist()
    war_2026 = data[data["window"].str.startswith("war_2026")]["avg_change_vs_own_pre_pct"].tolist()
    grouped_bar_svg(
        CHARTS / "brent_event_comparison.svg",
        "Brent price shock: Twelve-Day War vs 2026 Hormuz crisis",
        labels,
        [{"name": "2025 十二日战争", "values": twelve}, {"name": "2026 霍尔木兹危机", "values": war_2026}],
        "Change vs own pre-war average (%)",
    )


def make_hormuz_exposure_chart() -> None:
    data = pd.read_csv(OUT / "iran_hormuz_exposure_annual_shares.csv", encoding="utf-8-sig")
    data = data[(data["year"] >= 1995) & (data["year"] <= 2025)].copy()
    series = [
        {"name": "海湾来源合计", "x": data["year"].tolist(), "y": data["gulf_total_ex_oman_yemen"].tolist()},
        {"name": "非海湾替代来源", "x": data["year"].tolist(), "y": data["non_gulf_substitutes"].tolist()},
        {"name": "直接伊朗", "x": data["year"].tolist(), "y": data["direct_iran"].tolist()},
    ]
    line_svg(CHARTS / "hormuz_exposure_annual.svg", "Singapore oil-import exposure by source group", series, "Share (%)")


def make_q1_reallocation_chart() -> None:
    data = pd.read_csv(OUT / "iran_hormuz_exposure_q1_shares.csv", encoding="utf-8-sig").set_index("year")
    labels = ["海湾核心", "Saudi/UAE", "东南亚/澳洲", "亚洲炼化", "美洲"]
    cols = [
        "hormuz_core_no_large_bypass",
        "gulf_with_bypass_capacity",
        "regional_se_asia_oceania",
        "asian_refinery_trade",
        "americas",
    ]
    grouped_bar_svg(
        CHARTS / "q1_2026_gulf_reallocation.svg",
        "2026Q1 oil-import source reallocation",
        labels,
        [
            {"name": "2025Q1", "values": [data.loc[2025, col] for col in cols]},
            {"name": "2026Q1", "values": [data.loc[2026, col] for col in cols]},
        ],
        "Share (%)",
    )


def make_static_index() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    DOC_ASSETS.mkdir(parents=True, exist_ok=True)
    for chart in [
        "singapore_maritime_index.svg",
        "bunker_fuel_mix_share.svg",
        "brent_event_comparison.svg",
        "hormuz_exposure_annual.svg",
        "q1_2026_gulf_reallocation.svg",
    ]:
        copyfile(CHARTS / chart, DOC_ASSETS / chart)
    html = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Singapore Maritime Energy Analytics</title>
  <style>
    body { margin: 0; font-family: Arial, "Microsoft YaHei", sans-serif; color: #17202a; background: #f7f9fb; }
    header { padding: 42px 7vw 28px; background: #102a43; color: white; }
    main { padding: 28px 7vw 48px; }
    h1 { margin: 0 0 12px; font-size: 34px; }
    h2 { margin: 34px 0 12px; font-size: 22px; }
    p { line-height: 1.65; max-width: 980px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-top: 16px; }
    .metric { background: white; border: 1px solid #d9e2ec; border-radius: 8px; padding: 16px; }
    .metric b { display: block; font-size: 24px; margin-bottom: 6px; color: #0b5cad; }
    figure { margin: 18px 0; padding: 14px; background: white; border: 1px solid #d9e2ec; border-radius: 8px; }
    img { width: 100%; height: auto; display: block; }
    a { color: #0b5cad; }
  </style>
</head>
<body>
  <header>
    <h1>Singapore Maritime Energy Analytics</h1>
    <p>用新加坡官方港口数据、油品进口市场数据、Brent 油价和 PortWatch 日度到港数据，分析港口大船化、燃料转型与伊朗/霍尔木兹风险传导。</p>
  </header>
  <main>
    <section class="grid">
      <div class="metric"><b>1995-2025</b>长期港口与能源枢纽样本窗口</div>
      <div class="metric"><b>+485.5%</b>到港船舶总吨位增长</div>
      <div class="metric"><b>36.0%</b>2025 年油品进口海湾来源份额</div>
      <div class="metric"><b>38.8%</b>2026Q1 海湾来源份额</div>
    </section>
    <p><strong>Historical May 2026 snapshot.</strong> Q1 source changes are descriptive; do not infer war causality. <a href="../METHODOLOGY.md">Methodology</a>.</p>\n    <h2>核心图表</h2>
    <figure><img src="assets/singapore_maritime_index.svg" alt="Singapore maritime index"></figure>
    <figure><img src="assets/bunker_fuel_mix_share.svg" alt="Bunker fuel mix"></figure>
    <figure><img src="assets/brent_event_comparison.svg" alt="Brent event comparison"></figure>
    <figure><img src="assets/hormuz_exposure_annual.svg" alt="Hormuz exposure annual"></figure>
    <figure><img src="assets/q1_2026_gulf_reallocation.svg" alt="Q1 2026 source reallocation"></figure>
    <h2>报告</h2>
    <p>主要报告见 <a href="../analysis/output/singapore_maritime_energy_story.md">Singapore maritime energy story</a>、
    <a href="../analysis/output/twelve_day_vs_2026_comparison.md">事件对比</a> 和
    <a href="../analysis/output/iran_hormuz_exposure_story.md">霍尔木兹暴露故事</a>。</p>
  </main>
</body>
</html>
"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    make_brent_event_chart()
    make_hormuz_exposure_chart()
    make_q1_reallocation_chart()
    make_static_index()
    print("Generated resume charts and docs/index.html")


if __name__ == "__main__":
    main()
