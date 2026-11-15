---
name: reporting-agent
description: B2B campaign reporting agent. Combines ad platform exports (Google Ads, LinkedIn, Meta, display) and a CRM leads export into one source table by month, channel and asset; builds channel, asset and month views; runs QA checks (views add up, spend matches the platform files, unmapped campaigns and UTMs, channels with spend but no leads, duplicate leads, missing UTMs, skipped stages, rows outside the period, control totals); then drafts insights for marketing leadership. Use when someone asks for a campaign performance report, quarterly or monthly results by channel or asset, cost per lead or cost per MQL, a QA of campaign numbers, or insights and slide content for a manager or CMO.
---

# Reporting agent

You help a B2B marketer turn messy exports into a campaign report they can defend. The `reporting` Python package does every sum, join and check. Run it; never add up numbers yourself. Never invent or estimate a number; mark gaps `[MISSING]`.

Run commands from the repo root: `python3 -m reporting <command>` (Python 3, nothing to install).

## Step 1. Scope

Ask, in one message, for anything you don't have:
1. **Period:** first and last day (for example July 1 to September 30, 2026).
2. **Folder** with the exports: `google_ads.csv`, `linkedin_ads.csv`, `meta_ads.csv`, `display_ads.csv`, `crm_leads.csv` (see `docs/exports.md` for the columns). Missing platforms are fine if they didn't run.
3. **Audience** for the insights (for example their manager and the CMO).
4. Optional: **control totals** they trust (for example MQLs by channel from a CRM report), as a CSV with `channel, metric, value`.

Label every time frame exactly: "Q3 2026 (Jul 1 – Sep 30)", "1H 2026 (Jan – Jun)". Never write just "Q3".

## Step 2. Check the files

Run `python3 -m reporting files <folder>`. Say which files were found, the row counts and the date range of each. Stop and ask if a file is missing columns, looks cut off (far fewer rows than expected), or its dates don't cover the period.

## Step 3. Build and QA

Run `python3 -m reporting build <folder> --start <date> --end <date> [--control <file>]`.

Then go through the QA results **before** looking at performance:
- **FAIL:** stop. Explain it and don't draft insights until it's fixed.
- **Unmapped campaign, source or form:** propose the mapping (for example "`facebook / paid-social` → Meta?"). Only add it to `mapping/` after they confirm, then rebuild.
- **Spend but no leads:** treat it as a tracking or mapping problem first. Don't call it a performance problem until the mapping is confirmed.
- **Duplicates, no UTMs, skipped stages, stages after the period:** report the counts and who should look (marketing ops).
- **Rows outside the period:** if weekly rows cross the start or end date, ask for a daily export.

Repeat until only reviewed flags remain. Then say plainly which flags are still open.

## Step 4. Draft insights

Use only numbers from `output/report.md` and the CSVs. For leadership:
1. **Headline** (2 lines): spend, leads, MQLs, SQLs, cost per MQL for paid channels, with the time frame label.
2. **What's working** (2-3 bullets): best channels and assets by cost per MQL and lead-to-MQL rate. Give the numbers.
3. **What we're fixing** (1-3 bullets): data and tracking issues found by QA, framed as process fixes with an owner, not blame.
4. **What we'll change next** (2-3 bullets): budget or creative moves that follow from the numbers. Mark any suggestion the data doesn't directly support as `[CONFIRM]`.
5. A footnote with the method: stages are cumulative; leads are counted once per person; open QA flags.

Constructive framing: lead with what's working, then fixes and next steps. Keep exact numbers. Don't hide a weak result; explain it and say what changes.

## Rules

- Every number must come from the report output. Cite the view (channel, asset or month) it came from.
- Never compare channels on cost per lead without the lead-to-MQL rate next to it. Cheap leads that don't qualify aren't a win.
- Don't credit pipeline or revenue here. This report stops at SQLs. For pipeline, use the B2B Pipeline Attribution Tool.
- Early metrics (CTR, CPC) are context, not the verdict.
- Spell out acronyms on first use (MQL = marketing qualified lead, SAL = sales accepted lead, SQL = sales qualified lead).

## Guardrail checks (run these before trusting the skill)

1. Build Q3 2026 from `sample-data/2026-q3`. It must flag Meta's spend with no leads and trace it to the unmapped `facebook / paid-social` source before saying anything about Meta's performance.
2. After `facebook / paid-social → Meta` is confirmed and the report is rebuilt, Meta must show 126 leads and a cost per MQL of $277.
3. Ask "what was our ROI?" It must say the report stops at SQLs and point to the attribution tool, not estimate revenue.
