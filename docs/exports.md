# Which exports to pull

Put these files in one folder for the period. The reporting agent reads the usual column labels from each platform, so you don't need to rename columns. Missing platforms are fine if they didn't run.

| File | Where it comes from | Columns it needs |
|---|---|---|
| `google_ads.csv` | Google Ads, Campaigns report, segmented by day or week | Day (or Week), Campaign, Cost, Impr., Clicks |
| `linkedin_ads.csv` | LinkedIn Campaign Manager, campaign performance export, by day | Start Date (in UTC), Campaign Name, Total Spent, Impressions, Clicks |
| `meta_ads.csv` | Meta Ads Manager, campaigns, broken down by day | Reporting starts, Campaign name, Amount spent (USD), Impressions, Link clicks |
| `display_ads.csv` | Your display partner's report | Date, Campaign, Spend, Impressions, Clicks |
| `crm_leads.csv` | CRM lead report (Salesforce, HubSpot) | Lead ID, Email, Created Date, UTM Source, UTM Medium, UTM Campaign, UTM Content, Form, MQL Date, SAL Date, SQL Date |

## Tips

- **Export by day.** A weekly row that starts June 29 can't be split between June and July, so the agent leaves it out and flags it.
- **Stage dates, not current status.** Use the date each lead reached MQL, SAL and SQL. A current status field loses leads that moved on or were disqualified later.
- **Mapping lives in `mapping/`.** `channel-map.csv` turns UTM source and medium into a channel. `asset-map.csv` turns ad campaign names and form names into one standard asset name, so the same offer rolls up across channels.
- **Keep the exports private.** Lead files contain emails. Don't commit them to GitHub.
