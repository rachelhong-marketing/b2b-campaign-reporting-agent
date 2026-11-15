"""Command line: files, build."""
import argparse
from datetime import date
from pathlib import Path

from . import load, build, qa, report

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser(prog="reporting", description="Build a checked B2B campaign performance report.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("files", help="list the files found, row counts and missing columns")
    f.add_argument("folder")
    b = sub.add_parser("build", help="build the source table, views, QA and report")
    b.add_argument("folder")
    b.add_argument("--start", required=True, help="first day of the period, e.g. 2026-07-01")
    b.add_argument("--end", required=True, help="last day of the period, e.g. 2026-09-30")
    b.add_argument("--out", help="output folder (default: <folder>/output)")
    b.add_argument("--control", help="optional control totals CSV: channel, metric, value")
    b.add_argument("--channel-map", default=str(ROOT / "mapping" / "channel-map.csv"))
    b.add_argument("--asset-map", default=str(ROOT / "mapping" / "asset-map.csv"))
    a = ap.parse_args(argv)

    folder = Path(a.folder)
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        return 2
    ads, ad_notes = load.read_ads(folder)
    leads, lead_notes = load.read_leads(folder)

    if a.cmd == "files":
        print(f"Files in {folder}\n")
        for name, (platform, _) in load.AD_FILES.items():
            n = sum(1 for r in ads if r["file"] == name)
            dates = sorted(r["date"] for r in ads if r["file"] == name and r["date"])
            span = f"{dates[0]} to {dates[-1]}" if dates else "-"
            print(f"  {name:<20} {platform:<11} {n:>4} rows   dates {span}")
        print(f"  {load.LEADS_FILE:<20} {'CRM':<11} {len(leads):>4} rows")
        for n in ad_notes + lead_notes:
            print(f"  NOTE {n}")
        return 0

    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    rows, facts = build.build(ads, leads, load.read_map(a.channel_map), load.read_map(a.asset_map), start, end)
    control = load.read_control(a.control) if a.control else None
    checks = qa.run(rows, facts, ad_notes, lead_notes, control)
    out = Path(a.out) if a.out else folder / "output"
    files = report.write_csvs(rows, out)
    label = load.period_label(start, end)
    (out / "report.md").write_text(report.markdown(rows, checks, label), encoding="utf-8")

    fails = sum(1 for c in checks if c[0] == "FAIL")
    flags = sum(1 for c in checks if c[0] == "FLAG")
    print(f"Report: {label}")
    print(f"QA: {fails} failed, {flags} flagged, {len(checks) - fails - flags} passed")
    for status, check, detail in checks:
        if status != "PASS":
            print(f"  {status:<5}{check}: {detail}")
    print(f"\nSaved to {out}/: report.md, " + ", ".join(files))
    return 1 if fails else 0
