# 40 · Packets (anti-clog)

LLM bundles are **budgets**, not catalogs. Dumping the comprehensive map, a node’s full mx list, or the ~46 MB V15 blob is a defect (P-LLM-CLOG, P-UNWIRED-LAYERS). Overflow: truncate and log. Do not “include a bit more.” Empty AI is not a reason to enlarge the packet.

## hinge_pack(unit_id)

Schema `awm.hinge_pack.v1`.

```
map.statements[unit_id]     # decision_hinge, mechanism, mx[], mx_na
enrichment where unit_id ∈ serves_statement_ids   # cap 8, typed
witness mx (enrichment-attested, not on the derived list) for that UID
```

Join is string equality on `unit_id` (`science/grade_11/chem_ch_106/H001`). Not embedding. Not `primary_node_id`. Not a dump of every mx on the node.

## Caps

| Layer | Cap |
|---|---|
| T-SEL nodes | closed list, id+label only; prompt ≤2k chars |
| T-UNIT candidates | ≤64 after deterministic chapter/subject filter; text ≤2k |
| Hinges in a lesson digest | 8 |
| Enrichment rows | 8 |
| Journal overlay rows | 8 |
| Mx per hinge into a prompt | that hinge’s list, not the 3,125-row catalog |
| Map slice for phy/bio | matching NCERT chapters; **mx: []** explicit |
| T-AUTHOR mx shown | ≤4 (type + canonical wrong output + status) |
| T-AUTHOR enrichment | ≤3 typed statements |
| T-SOLVE batch | ≤8 items; stem ≤900 chars + options + option-table + ≤6 map units |
| T-BRIEF total | three already-typeset packs, ≤6k tokens |
| S-FEED | ≤40 items of **this** paper; mx/ledger stripped at builder |
| T-MOD instruction | ≤1k; one item, whitelist fields only |

## Copy-only rule

Map `unit_id`s, nodes, mx `{type, cwo}`, and enrichment statements must be **copied from the packet**. If none fit: empty list. Do not invent ids. Do not invent DOIs. If enrichment `citation.url` is null, it stays null.

## Citation

If enrichment `citation.url` is null, do not invent a DOI.
