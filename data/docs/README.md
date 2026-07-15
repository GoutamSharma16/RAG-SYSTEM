# policy_data.txt

## Overview

This file is a plain-text export of a sample corporate policy database — 206 rows in the format **ID | Topic | Content**. It appears to be synthetic/demo data built for practicing Retrieval-Augmented Generation (RAG) pipelines: the final row is explicitly labeled *"Final Row Check"* and describes itself as a *"200-row sample corporate policy database for beginner RAG practice."*

## Format

The data is **not** a clean delimited table (no CSV commas or tabs) — it's raw, wrapped plain text where each record spans multiple lines:

```
ID   Topic            Content
                       <content line 1>
                       <content line 2>
     <Topic label>     <content line 3>
   <ID><Topic cont.>   <content line N>
```

Because the source was likely copy-pasted from a rendered table (e.g., a PDF or web page), columns are visually aligned with whitespace rather than structured with delimiters, and the ID/Topic/Content text often wraps awkwardly across lines. **This file is meant to be parsed programmatically, not read top-to-bottom.**

## Fields

| Field | Description |
|---|---|
| **ID** | Sequential row number (1–206) |
| **Topic** | A short category label, e.g. `Remote Work Policy`, `Health Insurance`, `Wi-Fi Access`, `Expense Reimbursement`, `PTO`, `IT Support`, `Office Security`, `Time Off & Leave`, `Benefits & Perks`, `Performance & Growth`, `Payroll`, `Legal`, `Procurement` |
| **Content** | 1–3 sentences of policy text. Many entries include a trailing `[Ref Code: OX-####]` tag, which appears to be an internal reference/citation ID used to test whether a RAG system correctly retrieves and cites the right source chunk |

## Notable characteristics

- **Recurring topics with conflicting values**: several topics (e.g., "Remote Work Policy" / "Remote Work & Hours", "Time Off (PTO)" / "Time Off & Leave") repeat with *different* numeric details (e.g., PTO accrual stated as both 1.5 days/month and 3 days/month; core hours stated as both 10 AM–3 PM and 9 AM–4 PM). This is likely intentional — a common RAG stress-test to see if retrieval picks the most recent/correct version rather than an outdated one.
- **Ref Codes**: ~31+ entries carry `[Ref Code: OX-####]` tags for traceability/citation testing.
- **Sensitive-looking sample data**: includes fake Wi-Fi network names/passwords, support phone numbers, and internal contacts — these are placeholder/synthetic values for demo purposes, not real credentials.
- **Wide topic range**: covers HR (PTO, parental/bereavement/sabbatical leave, payroll, benefits), IT (hardware, VPN, MFA, software updates, browser policy), office/physical security (badges, tailgating, visitor registration), and legal/procurement policies.

## Suggested use

To work with this file programmatically, first reconstruct each record by regex/pattern rather than fixed-width columns — e.g., split on the leading `ID<Topic>` pattern that appears at the start of each record's last content line, then join the wrapped lines above it. Once parsed into structured `{id, topic, content, ref_code}` records, the data is well-suited for:
- Chunking and embedding for a RAG demo
- Testing retrieval accuracy against near-duplicate/conflicting topics
- Practicing citation/reference-code matching