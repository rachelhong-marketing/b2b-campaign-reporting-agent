# B2B Campaign Reporting Agent

> **B2B Campaign Lifecycle Toolkit**, step 6 of 7
>
> [1. Position](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) → [2. Plan](https://github.com/rachelhong-marketing/b2b-campaign-assistant) → [3. Content](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) → [4. Set up](https://github.com/rachelhong-marketing/b2b-paid-media-planner) → [5. Test](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) → **6. Report** → [7. Prove](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool)

B2B campaign data is scattered. Spend, impressions and clicks sit in each ad platform (Google Ads, LinkedIn, Meta, display). Leads, and how far they move from lead to MQL (marketing qualified lead), SAL (sales accepted lead) and SQL (sales qualified lead), sit in the CRM. Putting it together by hand is slow, and the gaps between systems are easy to miss.

This AI agent consolidates every source into one file, with one row per month, channel and asset that shows spend, clicks and each funnel stage side by side. It adds up results across channels, checks every channel and funnel stage for data gaps and tracking problems **before** anyone reads the numbers, and then drafts insights for leadership.

It runs as a Claude Code skill, with Python doing every sum, join and check. There's also a Microsoft Copilot version.

All data here is made up.

## What you give it, and what you get back

### What you give it

Put these exports in one folder for the period. [docs/exports.md](docs/exports.md) shows which columns each needs.

| You provide | Where it comes from |
|---|---|
| Google Ads export | Campaigns report, by day or week |
| LinkedIn export | Campaign Manager performance export |
| Meta export | Ads Manager campaigns, by day |
| Display export | Your display partner's report |
| CRM leads | Salesforce or HubSpot lead report with UTMs and the dates each lead became MQL, SAL and SQL |
| Mapping files | Which UTM source and medium means which channel, and which campaign names are the same asset ([`mapping/`](mapping/)) |
| Trusted CRM totals (optional) | Totals to compare the report against |

### What you get back

| Output | What it looks like | Example |
|---|---|---|
| One source table | One row per month, channel and asset: spend, clicks, leads, MQLs, SALs, SQLs | [source_table.csv](examples/2-after-mapping-fix/source_table.csv) |
| Views | Totals by channel, by asset and by month, all added up from the source table | [by_channel.csv](examples/2-after-mapping-fix/by_channel.csv) |
| QA report | Every data gap and tracking problem found, before anyone reads the numbers | [first run](examples/1-first-run/report.md) |
| Fixed report | The same report after you approve a mapping fix | [after the fix](examples/2-after-mapping-fix/report.md) |
| Leadership insights | Headline, what's working, what we're fixing and who owns it, what we'll change next | [Insights](examples/3-leadership-insights.md) |

## Why QA comes first

On the sample data, the first run shows Meta with **$8,585 in spend and zero leads**. A quick read says "cut Meta." The QA check says something else: 126 leads came in tagged `facebook / paid-social`, which isn't in the channel map. Once that's mapped, Meta has the **lowest cost per MQL of any channel ($277)**.

| | First run | After the mapping fix |
|---|---|---|
| Meta leads | 0 | 126 |
| Meta cost per MQL | none | $277 (lowest of any channel) |
| Paid channels' cost per MQL | $542 | $469 |

That's the problem this agent solves. Most reporting mistakes are tracking and mapping problems that look like performance problems. The agent finds them first, asks before fixing a mapping, rebuilds, and only then writes insights.

## What it does

1. **Checks the files:** which exports are there, row counts and date ranges.
2. **Builds one source table:** one row per month × channel × asset, with spend, impressions, clicks, leads, MQLs, SALs and SQLs. Every view is summed from it; nothing is typed by hand.
3. **Runs QA:**

| Check | What it catches on the sample data |
|---|---|
| Views add up | Channel, asset and month totals equal the source table |
| Spend matches the platform files | $108,903.79 in both |
| Unmapped ad campaigns | A LinkedIn carousel test ($5,084) not in the asset map |
| Unmapped lead sources | 126 leads tagged `facebook` instead of `meta` |
| Unmapped forms | `records-video-cta-v2` (4 leads) |
| Spend but no leads | Meta, before the mapping fix |
| Duplicate leads | 6 repeat form fills counted once |
| No UTMs | 14 leads (2%) |
| Skipped stages | A lead with an SQL date but no MQL date (counted as an MQL, since stages are cumulative) |
| Stages after the period | 82 stage changes after September 30, not counted |
| Rows outside the period | A weekly Google row starting June 29 |
| Control totals (optional) | Any channel where the report and a trusted CRM total differ |

4. **Drafts insights** in a fixed shape for leadership: headline, what's working, what we're fixing (with owners), what we'll change next. See [the example](examples/3-leadership-insights.md).

## Use it with Claude Code

Download the repo, open the folder in Claude Code, and ask:

- "Build the Q3 2026 report from sample-data/2026-q3."
- "Why does Meta show no leads?"
- "Write the Q3 summary for my manager and the CMO."

The skill is in [`.claude/skills/reporting-agent/SKILL.md`](.claude/skills/reporting-agent/SKILL.md). For your own data, follow [docs/exports.md](docs/exports.md) and update the maps in [`mapping/`](mapping/).

## Use it in Microsoft Copilot

[`copilot/`](copilot/) has the same agent as Copilot instructions and a setup guide. Copilot does the math itself, so the guide explains what to check in its QA tab.

## Command line

Python 3 only, nothing to install.

```bash
python3 -m reporting files sample-data/2026-q3
python3 -m reporting build sample-data/2026-q3 --start 2026-07-01 --end 2026-09-30 --out my-report
python3 -m reporting build sample-data/2026-q3 --start 2026-07-01 --end 2026-09-30 --control my-control-totals.csv
python3 -m unittest discover -s tests
```

Output: `report.md` plus `source_table.csv`, `by_channel.csv`, `by_asset.csv` and `by_month.csv`. Both example runs are in [`examples/`](examples/): [the first run](examples/1-first-run/report.md) and [after the mapping fix](examples/2-after-mapping-fix/report.md).

## How the numbers are counted

- Leads: one per person (by email), by created date in the period.
- Stages are cumulative: an SQL also counts as an MQL and a SAL. A stage counts if it was reached by the period end.
- Channel comes from UTM source and medium; asset from the ad campaign name or the form. Anything not mapped shows as [UNMAPPED], so it's visible instead of dropped.
- The headline cost per MQL uses paid channels only.
- The report stops at SQLs. For pipeline, use step 7, the attribution tool.

## The B2B Campaign Lifecycle Toolkit

Seven tools, one per step of a B2B campaign, from positioning to proving pipeline. Each works on its own; together they cover the whole cycle. All sample data is made up.

| Step | Tool | What it does |
|---|---|---|
| 1. Position | [B2B Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) | Assist the product marketer: draft ideal customer profile hypotheses from deals, target accounts and sales notes, plus persona guides, positioning and messaging pillars backed by approved proof. The product marketer decides. |
| 2. Plan | [B2B Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) | Turn the positioning into a campaign theme, write the campaign plan and master brief, then draft channel briefs, keywords, landing page and ad copy, all checked before launch. |
| 3. Content | [B2B Content Strategy Assistant](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) | Pick content topics inside the campaign theme from audience questions, news, competitors and keyword data, outline and check each piece so search and AI answer tools can quote it, and log whether AI answers cite you. |
| 4. Set up | [B2B Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner) | Plan channels and retargeting, then build and check tracking links before launch. |
| 5. Test | [B2B Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) | Plan tests in waves, let the ad platform call the winner, check MQLs, and size tests when volume is small. |
| 6. Report | **B2B Campaign Reporting Agent** (this repo) | Consolidate ad platform and CRM data into one file, check every channel and funnel stage for gaps, and draft insights. |
| 7. Prove | [B2B Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) | Check the CRM data can be trusted, then show sourced and influenced pipeline. |

### Which tool is for your role

Teams are organized by function, and the steps cut across them. Start here:

| If you are a... | Start with |
|---|---|
| Product marketer | [1. Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) |
| Demand gen or campaign manager | [2. Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant), [4. Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner), [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) |
| Content marketer | [3. Content Strategy Assistant](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) |
| Paid media manager | [4. Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner), [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) |
| Marketing operations or analytics | [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner), [6. Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent), [7. Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) |

## About the author

**Rachel Hong** has worked in B2B demand generation and marketing analytics for more than ten years, at marketing and advertising technology companies. She builds campaigns, reporting and the AI workflows that help marketing teams plan and measure them.

[LinkedIn](https://www.linkedin.com/in/rachelhongatbaruch/)
