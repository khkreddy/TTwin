# 05 · Vision — two models, one kernel

TeacherTwin is an assessment world model on a static site: a machine-readable curriculum map, a tagged question bank, and the learner state those questions can reveal. It is not a chatbot with a corpus attached.

Most of the work is already done. Questions were ingested, tagged, typeset, and figure-encoded offline. The chemistry map already carries hinges, mechanism cores, and CANDIDATE mix-ups. Enrichment already sits in its own home. Heavy model use already happened in those pipelines. The live site’s job is to **retrieve and present** that capital, and to call AI only where a lookup cannot exist.

## What the Teacher Model is

The complete set of admissible acts while serving the teacher: retrieve, typeset, plan, ground fuzzy intent against closed lists, author CANDIDATE items, modify items session-only, first-write solution analyses, bind journal notes, brief. It is not a persona prompt. It is slots, packets, and refusals. Mix-ups stay on this side of the glass.

## What the Student Model is

The complete set of admissible acts while serving a learner: present the paper as assembled, collect responses, score deterministically, and — only after Finish — return one AI feedback pass. Every instructional invariant (I1–I20) lives here, because the learner surface is where false positives for learning are manufactured.

## Why personas, not two products

There is one store, one identity grammar, one scoring law, one ledger. Teacher and Student are two lenses with different field bans over the same state. Two products would fork state; forked state means two truths about the same item.

## TRACE-OR-LABEL

Every string that reaches a learner must be one of three sources:

1. a deterministic lookup,
2. a typeset field from the learner whitelist,
3. a labeled AI draft.

It must carry none of: mix-up ledger content, answer keys before Finish, criterion donation, frequency claims, vendor names.

Fail any clause: the string does not ship. There is no fourth source.

## What “high-quality focused support” means

AI synthesizes against a **capped packet** from the corpus we already have:

- a closed node list, not the map,
- `hinge_pack(unit_id)`, not a node dump,
- a solution-analysis slice, not a chat about the item,
- a scored paper, not a live tutor during the sitting.

If the packet does not contain the fact, the model may not say the fact.
