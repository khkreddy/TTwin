# 40 · Packets (anti-clog)

LLM bundles are **budgets**, not catalogs. Dumping the comprehensive map, a node’s full mx list, or 46 MB V15 is a defect (`P-LLM-CLOG`, `P-UNWIRED-LAYERS`).

## hinge_pack(unit_id)

```
map.statements[unit_id]     # decision_hinge, mechanism, mx[], mx_na
enrichment where unit_id ∈ serves_statement_ids   # cap 8, typed
witness mx (enrichment-attested, not on the derived list) for that UID
```

Join is string equality on `unit_id` (`science/grade_11/chem_ch_106/H001`). Not embedding. Not `primary_node_id`.

## Caps

| Layer | Cap |
|---|---|
| Hinges in a lesson digest | 8 |
| Enrichment rows | 8 |
| Journal overlay rows | 8 |
| Mx per hinge into a prompt | that hinge’s list, not the 3,125-row catalog |
| Map slice for phy/bio | matching NCERT chapters; mx empty |
| First-write analysis | stem ≤900 chars + options + ≤6 map units |

Overflow: truncate and log. Do not “include a bit more.”

## Citation

If enrichment `citation.url` is null, do not invent a DOI.
