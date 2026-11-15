# Campaign performance report: Q3 2026 (Jul 1 – Sep 30, 2026)

> QA: all hard checks passed. 7 item(s) flagged for review before sharing.

## Headline

- Spend $108,904 · 27,886 clicks · 862 leads · 261 MQLs · 95 SALs · 31 SQLs
- Paid channels only (LinkedIn, Paid Search, Display, Meta): cost per lead $140 · cost per MQL $469
- Stages are cumulative: an SQL is also counted as an MQL and a SAL.

## By channel

| Channel | Spend | Impressions | Clicks | Leads | MQLs | SALs | SQLs | CTR | CPC | Cost per lead | Cost per MQL | Lead to MQL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LinkedIn | $50,525 | 2,247,484 | 12,423 | 347 | 102 | 38 | 11 | 0.55% | $4.07 | $146 | $495 | 29% |
| Paid Search | $28,702 | 114,115 | 6,069 | 265 | 90 | 35 | 13 | 5.32% | $4.73 | $108 | $319 | 34% |
| Display | $21,092 | 2,348,099 | 2,800 | 40 | 9 | 4 | 0 | 0.12% | $7.53 | $527 | $2,344 | 22% |
| Meta | $8,585 | 730,479 | 6,594 | 126 | 31 | 7 | 4 | 0.90% | $1.30 | $68 | $277 | 25% |
| Email | $0 | 0 | 0 | 70 | 24 | 7 | 2 | - | - | - | - | 34% |
| Unattributed (no UTM) | $0 | 0 | 0 | 14 | 5 | 4 | 1 | - | - | - | - | 36% |
| **Total** | **$108,904** | **5,440,177** | **27,886** | **862** | **261** | **95** | **31** | **0.51%** | **$3.91** | **$126** | **$417** | **30%** |

## By asset

| Asset | Spend | Impressions | Clicks | Leads | MQLs | SALs | SQLs | CTR | CPC | Cost per lead | Cost per MQL | Lead to MQL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Data Readiness Assessment | $63,019 | 1,725,372 | 18,642 | 589 | 183 | 65 | 23 | 1.08% | $3.38 | $107 | $344 | 31% |
| Ready-or-Not Video | $40,802 | 3,529,525 | 8,219 | 190 | 50 | 20 | 5 | 0.23% | $4.96 | $215 | $816 | 26% |
| [UNMAPPED] 2026-Q3-DR-LinkedIn-Carousel-Test | $5,084 | 185,280 | 1,025 | 0 | 0 | 0 | 0 | 0.55% | $4.96 | - | - | - |
| Demo Request | $0 | 0 | 0 | 41 | 12 | 5 | 1 | - | - | - | - | 29% |
| 5 Signs Guide | $0 | 0 | 0 | 38 | 15 | 4 | 1 | - | - | - | - | 39% |
| [UNMAPPED] ready-video-cta-v2 | $0 | 0 | 0 | 4 | 1 | 1 | 1 | - | - | - | - | 25% |
| **Total** | **$108,904** | **5,440,177** | **27,886** | **862** | **261** | **95** | **31** | **0.51%** | **$3.91** | **$126** | **$417** | **30%** |

## By month

| Month | Spend | Impressions | Clicks | Leads | MQLs | SALs | SQLs | CTR | CPC | Cost per lead | Cost per MQL | Lead to MQL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07 | $32,556 | 1,672,665 | 8,128 | 239 | 75 | 35 | 18 | 0.49% | $4.01 | $136 | $434 | 31% |
| 2026-08 | $41,896 | 2,080,339 | 10,908 | 331 | 119 | 46 | 13 | 0.52% | $3.84 | $127 | $352 | 36% |
| 2026-09 | $34,452 | 1,687,173 | 8,850 | 292 | 67 | 14 | 0 | 0.52% | $3.89 | $118 | $514 | 23% |
| **Total** | **$108,904** | **5,440,177** | **27,886** | **862** | **261** | **95** | **31** | **0.51%** | **$3.91** | **$126** | **$417** | **30%** |

## QA

| Status | Check | Detail |
|---|---|---|
| PASS | Views add up to the source table | Channel, asset and month views match the source table for every metric. |
| PASS | Spend matches the platform files | $108,903.79 in the source table = $108,903.79 in the files (in period). |
| FLAG | Ad campaigns not in the asset map | LinkedIn '2026-Q3-DR-LinkedIn-Carousel-Test' ($5,084). Add them to mapping/asset-map.csv. |
| PASS | Lead sources not in the channel map | All UTM source and medium pairs mapped. |
| FLAG | Forms not in the asset map | 'ready-video-cta-v2' (4 leads). |
| PASS | Channels with spend but no leads | Every channel with spend has leads. |
| FLAG | Duplicate leads removed | 6 repeat record(s) for the same email were counted once. |
| FLAG | Leads with no UTMs | 14 leads (2%) have no UTM source; shown as 'Unattributed (no UTM)'. |
| FLAG | Leads that skipped a stage | 1 lead(s) reached SQL with no MQL date; counted as MQLs because stages are cumulative. Ask marketing ops why the date is missing (L0641). |
| FLAG | Stages reached after the period | 82 stage changes happened after the period end and are not counted in this report. |
| FLAG | Ad rows outside the period | 1 row(s) excluded (dates 2026-06-29), $2,178.44. If these are weekly rows that cross the start or end date, re-export by day. |

## How the numbers were built

- One source table, one row per month × channel × asset. Every view is summed from it; nothing is typed by hand.
- Spend, impressions and clicks come from each ad platform's export, filtered to the period by row date.
- Leads come from the CRM export, one per person (repeat records for the same email are counted once), by created date in the period. Channel comes from UTM source and medium; asset from the form.
- A stage counts if it was reached by the period end. Stages are cumulative.
- Channel and asset names come from `mapping/`. Anything not mapped shows as [UNMAPPED] so it's visible, not dropped.
- Cost per lead and cost per MQL divide spend by the leads in the same row. The headline uses paid channels only. Leads whose source isn't mapped can't be matched to spend, so fix mapping flags before reading cost per lead.
