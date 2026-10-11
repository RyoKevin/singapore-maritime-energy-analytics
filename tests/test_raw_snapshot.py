"""Optional regression tests for the historical May 2026 source ZIP.
Set MARITIME_SOURCE_ZIP to the full path of malacca_strait_data_package.zip.
The archive stays local and is never uploaded to GitHub.
"""
import csv
import io
import os
import unittest
import zipfile

ARCHIVE = os.environ.get("MARITIME_SOURCE_ZIP")
PREFIX = "malacca_strait_data_package/malacca_strait_data_package/"
GULF = {"Saudi Arabia", "United Arab Emirates", "Kuwait", "Qatar", "Bahrain"}


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@unittest.skipUnless(ARCHIVE, "Set MARITIME_SOURCE_ZIP to run raw-snapshot checks")
class RawSnapshotRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = zipfile.ZipFile(ARCHIVE)

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()

    @classmethod
    def csv_rows(cls, path):
        with cls.archive.open(PREFIX + path) as stream:
            return list(csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig")))

    @classmethod
    def annual(cls, filename, field, year):
        rows = cls.csv_rows("data/official_data_gov_sg/" + filename)
        return sum(number(r[field]) for r in rows if r["month"].startswith(str(year)))

    @classmethod
    def import_share(cls, months):
        rows = cls.csv_rows("data/official_data_gov_sg/merchandise_imports_oil_by_market_monthly.csv")
        total = sum(number(r[m]) for r in rows for m in months)
        gulf = sum(number(r[m]) for r in rows if r["DataSeries"] in GULF for m in months)
        return 100 * gulf / total

    def test_required_raw_files(self):
        files = set(self.archive.namelist())
        for name in ["bunker_sales_breakdown_monthly.csv", "bunker_sales_total_monthly.csv",
                     "cargo_throughput_total_monthly.csv", "container_throughput_monthly.csv",
                     "merchandise_imports_oil_by_market_monthly.csv",
                     "tanker_arrivals_total_monthly.csv", "vessel_calls_75gt_monthly.csv"]:
            self.assertIn(PREFIX + "data/official_data_gov_sg/" + name, files)
        for name in ("fred_brent_crude_oil.csv", "fetchseries_port_calls_by_country_fsr.xlsx"):
            self.assertIn(PREFIX + "raw/" + name, files)

    def test_port_growth_1995_to_2025(self):
        cases = [("cargo_throughput_total_monthly.csv", "cargo_throughput", 101.1),
                 ("container_throughput_monthly.csv", "container_throughput", 277.0),
                 ("bunker_sales_total_monthly.csv", "bunker_sales", 224.6),
                 ("vessel_calls_75gt_monthly.csv", "number_of_vessel_calls", 21.8),
                 ("vessel_calls_75gt_monthly.csv", "gross_tonnage", 485.5)]
        for filename, field, expected in cases:
            with self.subTest(field=field):
                first = self.annual(filename, field, 1995)
                last = self.annual(filename, field, 2025)
                self.assertAlmostEqual(100 * (last / first - 1), expected, delta=0.06)

    def test_gulf_origin_shares(self):
        def months(year, labels):
            return [str(year) + month for month in labels]
        q1 = ["Jan", "Feb", "Mar"]
        full = q1 + ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        checks = [(months(1995, full), 68.6), (months(2025, full), 36.0),
                  (months(2025, q1), 29.6), (months(2026, q1), 38.8),
                  (["2026Jan"], 37.7), (["2026Feb"], 45.0), (["2026Mar"], 35.5)]
        for period, expected in checks:
            with self.subTest(period=period):
                self.assertAlmostEqual(self.import_share(period), expected, delta=0.055)

    def test_brent_event_averages(self):
        rows = self.csv_rows("raw/fred_brent_crude_oil.csv")
        windows = [("2025-05-01", "2025-06-12", 65.66),
                   ("2025-06-13", "2025-06-24", 76.34),
                   ("2026-01-01", "2026-02-27", 68.69),
                   ("2026-02-28", "2026-03-31", 103.13),
                   ("2026-04-01", "2026-05-01", 117.33)]
        for begin, end, expected in windows:
            with self.subTest(window=(begin, end)):
                vals = [number(r["brent_price_usd"]) for r in rows
                        if begin <= r["date"] <= end and r["brent_price_usd"].strip() not in ("", "na")]
                self.assertTrue(vals)
                self.assertAlmostEqual(sum(vals) / len(vals), expected, delta=0.01)


if __name__ == "__main__":
    unittest.main()
