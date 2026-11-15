import csv
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from reporting import load, build, qa, cli
from reporting.build import pivot, total

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "sample-data" / "2026-q3"
START, END = date(2026, 7, 1), date(2026, 9, 30)


def run(channel_map=None, control=None):
    ads, an = load.read_ads(DATA)
    leads, ln = load.read_leads(DATA)
    cm = load.read_map(ROOT / "mapping" / "channel-map.csv") + (channel_map or [])
    rows, facts = build.build(ads, leads, cm, load.read_map(ROOT / "mapping" / "asset-map.csv"), START, END)
    return rows, {c[1]: c for c in qa.run(rows, facts, an, ln, control)}


class FirstRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.checks = run()
        cls.by_channel = {r["channel"]: r for r in pivot(cls.rows, ["channel"])}

    def test_totals(self):
        t = total(self.rows)
        self.assertEqual(t["leads"], 862)
        self.assertEqual(t["mqls"], 261)
        self.assertAlmostEqual(t["spend"], 108903.79, places=2)

    def test_views_add_up(self):
        self.assertEqual(self.checks["Views add up to the source table"][0], "PASS")
        self.assertEqual(self.checks["Spend matches the platform files"][0], "PASS")

    def test_meta_spend_no_leads_traced_to_mapping(self):
        self.assertEqual(self.by_channel["Meta"]["leads"], 0)
        self.assertIn("Meta", self.checks["Channels with spend but no leads"][2])
        self.assertIn("facebook / paid-social (126 leads)", self.checks["Lead sources not in the channel map"][2])

    def test_planted_flags(self):
        c = self.checks
        self.assertIn("Carousel-Test", c["Ad campaigns not in the asset map"][2])
        self.assertIn("ready-video-cta-v2", c["Forms not in the asset map"][2])
        self.assertIn("6 repeat", c["Duplicate leads removed"][2])
        self.assertIn("14 leads", c["Leads with no UTMs"][2])
        self.assertIn("2026-06-29", c["Ad rows outside the period"][2])

    def test_stages_cumulative(self):
        for r in self.rows:
            self.assertGreaterEqual(r["mqls"], r["sals"])
            self.assertGreaterEqual(r["sals"], r["sqls"])


class AfterMappingFix(unittest.TestCase):
    def test_meta_after_fix(self):
        rows, checks = run([{"utm_source": "facebook", "utm_medium": "paid-social", "channel": "Meta"}])
        meta = {r["channel"]: r for r in pivot(rows, ["channel"])}["Meta"]
        self.assertEqual(meta["leads"], 126)
        self.assertEqual(round(meta["cost_per_mql"]), 277)
        self.assertEqual(checks["Channels with spend but no leads"][0], "PASS")


class Control(unittest.TestCase):
    def test_control_mismatch_fails(self):
        _, checks = run(control={("Paid Search", "mqls"): 95, ("LinkedIn", "mqls"): 102})
        status, _, detail = checks["Matches control totals"]
        self.assertEqual(status, "FAIL")
        self.assertIn("Paid Search mqls: report 90 vs. control 95", detail)
        self.assertNotIn("LinkedIn", detail)


class Parsing(unittest.TestCase):
    def test_values(self):
        self.assertEqual(load.to_number("$1,568.84"), 1568.84)
        self.assertEqual(load.to_date("7/6/2026"), date(2026, 7, 6))
        self.assertEqual(load.period_label(START, END), "Q3 2026 (Jul 1 – Sep 30, 2026)")
        self.assertEqual(load.period_label(date(2026, 7, 1), date(2026, 8, 31)), "Jul 1 – Aug 31, 2026")


class Commands(unittest.TestCase):
    def test_build_writes_files(self):
        out = Path(tempfile.mkdtemp())
        try:
            with redirect_stdout(io.StringIO()):
                code = cli.main(["build", str(DATA), "--start", "2026-07-01", "--end", "2026-09-30", "--out", str(out)])
            self.assertEqual(code, 0)
            for f in ("report.md", "source_table.csv", "by_channel.csv", "by_asset.csv", "by_month.csv"):
                self.assertTrue((out / f).exists(), f)
        finally:
            shutil.rmtree(out)


if __name__ == "__main__":
    unittest.main()
