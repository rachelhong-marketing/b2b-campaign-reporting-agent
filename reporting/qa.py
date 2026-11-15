"""QA checks. Each returns (status, check, detail). FAIL means the numbers can't be shared yet."""
from collections import Counter

from .build import METRICS, UNMAPPED, NO_UTM, pivot, total

PASS, FLAG, FAIL = "PASS", "FLAG", "FAIL"


def run(rows, qa, ad_notes, lead_notes, control=None):
    out = []
    t = total(rows)

    # 1. Every view adds up to the source table
    views_ok = all(abs(sum(v[m] for v in pivot(rows, by)) - t[m]) < 0.01
                   for by in (["channel"], ["asset"], ["month"]) for m in METRICS)
    out.append((PASS if views_ok else FAIL, "Views add up to the source table",
                "Channel, asset and month views match the source table for every metric." if views_ok
                else "A view doesn't match the source table. Don't share until fixed."))

    # 2. Ad file totals in the period = source table
    file_spend = sum(f["spend"] for f in qa.get("ad_file_totals", {}).values())
    ok = abs(file_spend - t["spend"]) < 0.01
    out.append((PASS if ok else FAIL, "Spend matches the platform files",
                f"${t['spend']:,.2f} in the source table = ${file_spend:,.2f} in the files (in period)." if ok
                else f"Source table ${t['spend']:,.2f} vs. files ${file_spend:,.2f}."))

    # 3. Control totals (optional)
    if control:
        diffs = []
        by_channel = {r["channel"]: r for r in pivot(rows, ["channel"])}
        for (channel, metric), value in control.items():
            mine = by_channel.get(channel, {}).get(metric, 0)
            if abs(mine - value) > 0.5:
                diffs.append(f"{channel} {metric}: report {mine:,.0f} vs. control {value:,.0f}")
        out.append((FAIL if diffs else PASS, "Matches control totals",
                    "; ".join(diffs) if diffs else "Every control total matches."))

    # 4. Unmapped names
    camps = Counter()
    for platform, name, spend in qa.get("unmapped_campaigns", []):
        camps[(platform, name)] += spend
    if camps:
        detail = "; ".join(f"{p} '{n}' (${s:,.0f})" for (p, n), s in camps.items())
        out.append((FLAG, "Ad campaigns not in the asset map", detail + ". Add them to mapping/asset-map.csv."))
    else:
        out.append((PASS, "Ad campaigns not in the asset map", "All campaigns mapped."))
    srcs = Counter(qa.get("unmapped_sources", []))
    if srcs:
        detail = "; ".join(f"{s} / {m} ({n} leads)" for (s, m), n in srcs.items())
        out.append((FLAG, "Lead sources not in the channel map", detail + ". Add them to mapping/channel-map.csv, "
                                                                          "or fix the UTM at the source."))
    else:
        out.append((PASS, "Lead sources not in the channel map", "All UTM source and medium pairs mapped."))
    forms = Counter(qa.get("unmapped_forms", []))
    if forms:
        out.append((FLAG, "Forms not in the asset map",
                    "; ".join(f"'{f or '(blank)'}' ({n} leads)" for f, n in forms.items()) + "."))
    else:
        out.append((PASS, "Forms not in the asset map", "All forms mapped."))

    # 5. Spend with no leads, and the reverse
    by_channel = pivot(rows, ["channel"])
    no_leads = [c for c in by_channel if c["spend"] > 0 and c["leads"] == 0]
    out.append((FLAG if no_leads else PASS, "Channels with spend but no leads",
                ", ".join(f"{c['channel']} (${c['spend']:,.0f})" for c in no_leads)
                + ". Usually a UTM or mapping problem; check before calling it a performance problem." if no_leads
                else "Every channel with spend has leads."))

    # 6. Lead hygiene
    dups = qa.get("duplicate_leads", [])
    out.append((FLAG if dups else PASS, "Duplicate leads removed",
                f"{len(dups)} repeat record(s) for the same email were counted once." if dups else "None."))
    no_utm = qa.get("no_utm", [])
    out.append((FLAG if no_utm else PASS, "Leads with no UTMs",
                f"{len(no_utm)} leads ({len(no_utm) / max(t['leads'], 1):.0%}) have no UTM source; shown as '{NO_UTM}'."
                if no_utm else "None."))
    skipped = qa.get("skipped_stages", [])
    out.append((FLAG if skipped else PASS, "Leads that skipped a stage",
                f"{len(skipped)} lead(s) reached SQL with no MQL date; counted as MQLs because stages are cumulative. "
                f"Ask marketing ops why the date is missing ({', '.join(skipped[:5])})." if skipped else "None."))
    after = qa.get("stage_after_period", [])
    out.append((FLAG if after else PASS, "Stages reached after the period",
                f"{len(after)} stage changes happened after the period end and are not counted in this report." if after
                else "None."))

    # 7. Excluded rows
    outside = qa.get("ads_outside_period", [])
    if outside:
        dates = sorted({r["date"].isoformat() for r in outside})
        out.append((FLAG, "Ad rows outside the period",
                    f"{len(outside)} row(s) excluded (dates {', '.join(dates)}), ${sum(r['spend'] for r in outside):,.2f}. "
                    "If these are weekly rows that cross the start or end date, re-export by day."))
    for n in ad_notes + lead_notes:
        out.append((FAIL if "missing columns" in n else FLAG, "Files", n))
    if qa.get("bad_dates"):
        out.append((FLAG, "Unreadable dates", "; ".join(qa["bad_dates"][:5])))
    return out
