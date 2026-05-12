from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(relative_path: str) -> None:
    # 统一入口，便于 README 中给出一键复现命令。
    script = ROOT / relative_path
    print(f"\n=== Running {relative_path} ===")
    runpy.run_path(str(script), run_name="__main__")


def main() -> None:
    for script in [
        "analysis/singapore_maritime_energy_story.py",
        "analysis/us_iran_war_impact.py",
        "analysis/compare_twelve_day_vs_2026.py",
        "analysis/iran_hormuz_exposure_story.py",
        "analysis/generate_resume_assets.py",
        "analysis/generate_interactive_page.py",
    ]:
        run_script(script)


if __name__ == "__main__":
    main()
