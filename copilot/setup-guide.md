# Set up the Reporting Agent in Microsoft Copilot

For teams that work in Microsoft 365. About an hour for the basic version.

## How the pieces map

| In this repo (Claude Code) | In Copilot |
|---|---|
| `.claude/skills/reporting-agent/SKILL.md` | Agent **Instructions** (paste `agent-instructions.md`) |
| `mapping/channel-map.csv`, `mapping/asset-map.csv` | Excel files in a SharePoint folder added as **Knowledge** |
| `python3 -m reporting build` | Copilot builds the Excel file itself. Check the QA tab before sharing. |
| `docs/exports.md` | A short "which exports to pull" doc in the same folder |

## Steps

1. **Make a SharePoint folder** with: the channel map, the asset map, your lead stage definitions and `exports.md`.
2. In Copilot, choose **Create agent** → **Configure**.
3. **Name:** Reporting Agent. **Description:** Consolidates ad platform and CRM data into one checked report across channels and funnel stages (lead, MQL, SAL, SQL), then drafts leadership insights.
4. **Instructions:** paste from `agent-instructions.md` and fill in the brackets.
5. **Knowledge:** add the SharePoint folder. Turn on **Only use specified sources**.
6. **Conversation starters:** copy the four from `agent-instructions.md`.
7. Each period, attach that period's exports in the chat rather than storing them in Knowledge. Lead files contain personal data.

## Guardrail checks before sharing it
1. Attach ad files where one platform's leads use a UTM source that isn't in the channel map. It must flag spend with no leads as a tracking problem, not poor performance.
2. Ask for ROI. It must say the report stops at SQLs.
3. Give it a control total that doesn't match. It must list the difference.

## Known limits
- Copilot can add numbers wrong or drop rows in long files. That's why the Claude Code version does the math in code. In Copilot, always check the QA tab: view totals must equal the source table, and spend must equal the platform files.
- Instructions max 8,000 characters. Check Microsoft's current documentation for limits.
