"""Build one source table (month x channel x asset) from ad and lead data, then every view from it."""
from collections import OrderedDict, defaultdict

METRICS = ["spend", "impressions", "clicks", "leads", "mqls", "sals", "sqls"]
UNMAPPED = "[UNMAPPED]"
NO_UTM = "Unattributed (no UTM)"


def build(ads, leads, channel_map, asset_map, start, end):
    """Returns (source_rows, qa_facts)."""
    ch_lookup = {(r["utm_source"].lower(), r["utm_medium"].lower()): r["channel"] for r in channel_map}
    ad_lookup = {r["value"]: (r["channel"], r["standard_asset"]) for r in asset_map if r["type"] == "ad_campaign"}
    form_lookup = {r["value"]: r["standard_asset"] for r in asset_map if r["type"] == "lead_form"}
    table = defaultdict(lambda: dict.fromkeys(METRICS, 0.0))
    qa = defaultdict(list)

    # Ads
    in_period_by_file = defaultdict(lambda: dict.fromkeys(("spend", "impressions", "clicks"), 0.0))
    for r in ads:
        if r["date"] is None:
            qa["bad_dates"].append(f"{r['file']}: '{r['date_text']}' ({r['campaign']})")
            continue
        if not (start <= r["date"] <= end):
            qa["ads_outside_period"].append(r)
            continue
        if r["campaign"] in ad_lookup:
            channel, asset = ad_lookup[r["campaign"]]
        else:
            channel, asset = r["platform"], f"{UNMAPPED} {r['campaign']}"
            qa["unmapped_campaigns"].append((r["platform"], r["campaign"], r["spend"]))
        key = (r["date"].strftime("%Y-%m"), channel, asset)
        for m in ("spend", "impressions", "clicks"):
            table[key][m] += r[m]
            in_period_by_file[r["file"]][m] += r[m]
    qa["ad_file_totals"] = dict(in_period_by_file)

    # Leads: one row per person (first record by created date)
    seen = {}
    for r in sorted(leads, key=lambda x: (x["created"] or end, x["lead_id"])):
        if r["created"] is None:
            qa["bad_dates"].append(f"crm_leads.csv: lead {r['lead_id']} has no created date")
            continue
        if not (start <= r["created"] <= end):
            qa["leads_outside_period"].append(r["lead_id"])
            continue
        if r["email"] and r["email"] in seen:
            qa["duplicate_leads"].append((r["lead_id"], seen[r["email"]], r["email"]))
            continue
        seen[r["email"]] = r["lead_id"]
        if not r["utm_source"]:
            channel = NO_UTM
            qa["no_utm"].append(r["lead_id"])
        else:
            channel = ch_lookup.get((r["utm_source"], r["utm_medium"]))
            if channel is None:
                channel = f"{UNMAPPED} {r['utm_source']} / {r['utm_medium']}"
                qa["unmapped_sources"].append((r["utm_source"], r["utm_medium"]))
        asset = form_lookup.get(r["form"])
        if asset is None:
            asset = f"{UNMAPPED} {r['form'] or '(no form)'}"
            qa["unmapped_forms"].append(r["form"])
        # Stages are cumulative: reaching SQL counts as MQL and SAL too. Count stages reached by the period end.
        reached = {s: (r[f"{s}_date"] is not None and r[f"{s}_date"] <= end) for s in ("mql", "sal", "sql")}
        if reached["sql"] and not reached["mql"]:
            qa["skipped_stages"].append(r["lead_id"])
        later = False
        for s in ("sql", "sal", "mql"):
            later = later or reached[s]
            reached[s] = later
        for s in ("mql", "sal", "sql"):
            if r[f"{s}_date"] is not None and r[f"{s}_date"] > end:
                qa["stage_after_period"].append((r["lead_id"], s.upper()))
        key = (r["created"].strftime("%Y-%m"), channel, asset)
        table[key]["leads"] += 1
        table[key]["mqls"] += reached["mql"]
        table[key]["sals"] += reached["sal"]
        table[key]["sqls"] += reached["sql"]
        qa["lead_totals"] = qa.get("lead_totals", 0) + 1

    rows = [{"month": k[0], "channel": k[1], "asset": k[2], **v} for k, v in sorted(table.items())]
    return rows, qa


def pivot(rows, by):
    out = OrderedDict()
    for r in sorted(rows, key=lambda x: tuple(x[b] for b in by)):
        k = tuple(r[b] for b in by)
        agg = out.setdefault(k, dict.fromkeys(METRICS, 0.0))
        for m in METRICS:
            agg[m] += r[m]
    result = []
    for k, v in out.items():
        result.append({**dict(zip(by, k)), **v, **ratios(v)})
    return sorted(result, key=lambda x: -x["spend"] if x["spend"] else -x["leads"] / 1e9)


def total(rows):
    t = dict.fromkeys(METRICS, 0.0)
    for r in rows:
        for m in METRICS:
            t[m] += r[m]
    return {**t, **ratios(t)}


def ratios(v):
    div = lambda a, b: (a / b) if b else None
    return {"ctr": div(v["clicks"], v["impressions"]), "cpc": div(v["spend"], v["clicks"]),
            "cost_per_lead": div(v["spend"], v["leads"]) if v["spend"] else None,
            "cost_per_mql": div(v["spend"], v["mqls"]) if v["spend"] else None,
            "mql_rate": div(v["mqls"], v["leads"])}
