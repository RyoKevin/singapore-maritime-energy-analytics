from pathlib import Path
import csv
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "output"


def rows(filename):
    with (OUT / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class PublishedOutputsTest(unittest.TestCase):
    def test_pages_and_svgs_exist(self):
        for name in ["index.html", "interactive.html"]:
            self.assertTrue((ROOT / "docs" / name).is_file())
        for name in ["singapore_maritime_index.svg", "bunker_fuel_mix_share.svg",
                     "brent_event_comparison.svg", "hormuz_exposure_annual.svg",
                     "q1_2026_gulf_reallocation.svg"]:
            self.assertTrue((ROOT / "docs" / "assets" / name).is_file())

    def test_pages_use_matching_local_assets(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        for name in ["singapore_maritime_index.svg", "bunker_fuel_mix_share.svg",
                     "brent_event_comparison.svg", "hormuz_exposure_annual.svg",
                     "q1_2026_gulf_reallocation.svg"]:
            self.assertIn("assets/" + name, page)

    def test_q1_gulf_share_reconciles(self):
        by_year = {int(r["year"]): r for r in rows("iran_hormuz_exposure_q1_shares.csv")}
        self.assertEqual(set(by_year), {2025, 2026})
        for y in (2025, 2026):
            r = by_year[y]
            gulf = float(r["hormuz_core_no_large_bypass"]) + float(r["gulf_with_bypass_capacity"])
            self.assertTrue(math.isclose(gulf, float(r["gulf_total_ex_oman_yemen"]), abs_tol=1e-8))
            components = ["americas", "asian_refinery_trade", "direct_iran",
                          "gulf_with_bypass_capacity", "hormuz_core_no_large_bypass",
                          "near_gulf_not_core", "other", "regional_se_asia_oceania"]
            self.assertTrue(math.isclose(sum(float(r[x]) for x in components), 100, abs_tol=1e-7))
        self.assertAlmostEqual(float(by_year[2025]["gulf_total_ex_oman_yemen"]), 29.6092275, places=4)
        self.assertAlmostEqual(float(by_year[2026]["gulf_total_ex_oman_yemen"]), 38.8136871, places=4)

    def test_complete_year_flag(self):
        for r in rows("annual_key_metrics.csv"):
            y = int(r["year"])
            if y == 2026:
                self.assertNotEqual(int(float(r["months_observed"])), 12)


if __name__ == "__main__":
    unittest.main()
