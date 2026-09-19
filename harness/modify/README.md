# Modify harness

Agent law and contract for TTwin Test-maker Modify (slot T-MOD). This package replaces the brute-force modify packet with a compiled one: deterministic assembly of the item's intelligence, one bounded model call, deterministic gates.

## Load order for agents

1. `harness/83_MODIFY.md` — law. Read first; it binds everything below.
2. `harness/modify/MODIFY_SPEC.md` — packet fields, caps, result schema, gates G1–G8, the UNBOUND join path.
3. `harness/modify/schema/modify_packet.v1.json` and `harness/modify/schema/modify_result.v1.json` — the contracts. Build to the first; validate against the second.
4. `harness/modify/MODIFY_TASK.md` — the implementer task. Read if you are changing code.
5. `harness/modify/JOURNAL_G68_GROK.md` — **required** if you author Science 6–8 CANDIDATEs with `ingest`. Good/bad examples from owner review. Do not repeat those faults.
6. `harness/modify/EXAMPLES_G68.md` — short good/bad library (Force C is a good distractor; H001 a3/a4 are bad encodings).

Governing law outside this package: `00_PRECEDENCE.md`, `10_KERNEL.md`, `11_FREEZE.md`, `15_SLOTS.md`, `40_PACKETS.md`, `80_ISOGEN.md`, `82_LBS_COMPILER.md`, `isogen/ISO_GENERATION_PROTOCOL.md`. This package points; it does not restate them.

## What this is not

- Not a second runtime. Modify runs inside the existing kernel: assemble/typeset/score stay lookups; the slot and its budgets stay as `15_SLOTS.md` defines.
- Not a freeze. Nothing here mints a freeze uid or touches exam.v1, Lamport L20, live V15, or any map sha.
- Not a vendor integration. The UI says "AI".

## Entry points

CLI/JS entry points land with the implementer task (`MODIFY_TASK.md`). Until then this package is law plus schemas: `assembleModifyPacket` (kernel lookup), one model call, gate validation, session write or keep-original.
