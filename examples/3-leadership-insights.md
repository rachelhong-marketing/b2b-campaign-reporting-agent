# Example output: leadership insights

> What the reporting agent drafts for "Write the Q3 insights for my manager and the CMO," after the user confirmed `facebook / paid-social → Meta` and the report was rebuilt. Made-up campaign. Every number comes from [`2-after-mapping-fix/report.md`](2-after-mapping-fix/report.md).

## Q3 2026 Clean Customer Data campaign (Jul 1 – Sep 30)

**Headline:** $108,904 in paid media brought in 862 leads, 261 MQLs (marketing qualified leads) and 31 SQLs (sales qualified leads). Paid channels delivered MQLs at $469 each.

**What's working**
- **The Customer Data Cleanup Playbook is the strongest offer:** 589 leads and 183 MQLs at $344 per MQL, compared with $816 for the video. *(By asset)*
- **Paid search and Meta retargeting are the most efficient channels:** $319 and $277 per MQL. Search also converts the most leads to MQLs (34%). *(By channel)*
- **LinkedIn brings the most volume:** 102 MQLs at $495 each, the most of any channel. *(By channel)*

**What we're fixing**
- **Meta leads were tagged `facebook` instead of `meta`,** so Meta first showed $8,585 spend and zero leads. Once mapped, it's our lowest cost per MQL. Owner: paid social lead, to update the UTM template; marketing ops to add the mapping. *(QA)*
- **A LinkedIn carousel test ($5,084) isn't in the asset map,** so its spend isn't tied to an offer yet. Owner: paid social lead. *(QA)*
- **14 leads (2%) had no UTMs** and 6 repeat form fills were counted once. Owner: marketing ops. *(QA)*

**What we'll change next**
- **Shift display budget toward search and Meta retargeting.** Display cost $2,344 per MQL with 0 SQLs so far. [CONFIRM: display also builds the retargeting audience Meta uses, so test a smaller display budget rather than cutting it.]
- **Lead with the playbook on LinkedIn,** and use the video for awareness and retargeting pools only.
- **Read September again in November.** September's lead-to-MQL rate (23%) and 0 SQLs reflect stage lag: 82 stage changes landed after September 30. *(By month, QA)*

*Method: stages are cumulative (an SQL also counts as an MQL); leads are counted once per person by created date; open QA flags: carousel test mapping, one form name (`records-video-cta-v2`), 14 leads without UTMs. Pipeline isn't included here; see the B2B Pipeline Attribution Tool.*
