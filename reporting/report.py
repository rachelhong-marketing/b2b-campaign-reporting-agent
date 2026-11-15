"""Write the CSV views and a Markdown report."""
import csv
from pathlib import Path

from .build import METRICS, pivot, total

COLS = METRICS + ["ctr", "cpc", "cost_per_lead", "cost_per_mql", "mql_rate"]
LABELS = {"spend": "Spend", "impressions": "Impressions", "clicks": "Clicks", "leads": "Leads", "mqls": "MQLs",
          "sals": "SALs", "sqls": "SQLs", "ctr": "CTR", "cpc": "CPC", "cost_per_lead": "Cost per lead",
          "cost_per_mql": "Cost per MQL", "mql_rate": "Lead to MQL"}


def fmt(col, v):
    if v is None:
        return "-"
    if col in ("spend", "cpc", "cost_per_lead", "cost_per_mql"):
        return f"${v:,.0f}" if col != "cpc" else f"${v:,.2f}"
    if col in ("ctr", "mql_rate"):
        return f"{v:.2%}" if col == "ctr" else f"{v:.0%}"
    return f"{v:,.0f}"


def md_table(rows, keys):
    head = [k.capitalize() for k in keys] + [LABELS[c] for c in COLS]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        lines.append("| " + " | ".join([str(r[k]) for k in keys] + [fmt(c, r[c]) for c in COLS]) + " |")
    t = total(rows)
    lines.append("| " + " | ".join(["**Total**"] + [""] * (len(keys) - 1) + [f"**{fmt(c, t[c])}**" for c in COLS]) + " |")
    return "\n".join(lines) + "\n"


def write_csvs(rows, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    views = {"source_table.csv": (rows, ["month", "channel", "asset"]),
             "by_channel.csv": (pivot(rows, ["channel"]), ["channel"]),
             "by_asset.csv": (pivot(rows, ["asset"]), ["asset"]),
             "by_month.csv": (sorted(pivot(rows, ["month"]), key=lambda r: r["month"]), ["month"])}
    for name, (data, keys) in views.items():
        cols = keys + [c for c in COLS if c in data[0]] if data else keys
        with open(out / name, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in data:
                w.writerow([r[c] if not isinstance(r.get(c), float) else round(r[c], 4) for c in cols])
    return list(views)


def markdown(rows, checks, label):
    t = total(rows)
    paid = [c for c in pivot(rows, ["channel"]) if c["spend"] > 0]
    pt = total(paid)
    fails = [c for c in checks if c[0] == "FAIL"]
    flags = [c for c in checks if c[0] == "FLAG"]
    out = [f"# Campaign performance report: {label}", ""]
    if fails:
        out += ["> **Not ready to share.** " + f"{len(fails)} QA check(s) failed. See the QA section.", ""]
    else:
        out += [f"> QA: all hard checks passed. {len(flags)} item(s) flagged for review before sharing.", ""]
    out += ["## Headline", "",
            f"- Spend {fmt('spend', t['spend'])} · {fmt('clicks', t['clicks'])} clicks · "
            f"{fmt('leads', t['leads'])} leads · {fmt('mqls', t['mqls'])} MQLs · {fmt('sals', t['sals'])} SALs · "
            f"{fmt('sqls', t['sqls'])} SQLs",
            f"- Paid channels only ({', '.join(c['channel'] for c in paid)}): cost per lead "
            f"{fmt('cost_per_lead', pt['cost_per_lead'])} · cost per MQL {fmt('cost_per_mql', pt['cost_per_mql'])}",
            "- Stages are cumulative: an SQL is also counted as an MQL and a SAL.", "",
            "## By channel", "", md_table(pivot(rows, ["channel"]), ["channel"]),
            "## By asset", "", md_table(pivot(rows, ["asset"]), ["asset"]),
            "## By month", "", md_table(sorted(pivot(rows, ["month"]), key=lambda r: r["month"]), ["month"]),
            "## QA", "", "| Status | Check | Detail |", "|---|---|---|"]
    for status, check, detail in checks:
        out.append(f"| {status} | {check} | {detail} |")
    out += ["", "## How the numbers were built", "",
            "- One source table, one row per month × channel × asset. Every view is summed from it; nothing is typed by hand.",
            "- Spend, impressions and clicks come from each ad platform's export, filtered to the period by row date.",
            "- Leads come from the CRM export, one per person (repeat records for the same email are counted once), "
            "by created date in the period. Channel comes from UTM source and medium; asset from the form.",
            "- A stage counts if it was reached by the period end. Stages are cumulative.",
            "- Channel and asset names come from `mapping/`. Anything not mapped shows as [UNMAPPED] so it's visible, not dropped.",
            "- Cost per lead and cost per MQL divide spend by the leads in the same row. The headline uses paid channels only. Leads whose source isn't mapped can't be matched to spend, so fix mapping flags before reading cost per lead."]
    return "\n".join(out) + "\n"
