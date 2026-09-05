# TTwin harness — Teacher Model and Student Model

These files are **agent law** for the live site (https://khkreddy.github.io/TTwin/). An agent loads them as the harness when the site goes live. They are not a second runtime and they do not fork state.

**Read order (mandatory).** An agent that has not read `15_SLOTS.md` may not call AI.

1. `00_PRECEDENCE.md` — collision order, freeze > deterministic > kernel > honesty, load contract
2. `05_VISION.md` — first principles, TRACE-OR-LABEL
3. `10_KERNEL.md` + `11_FREEZE.md` — shared deterministic kernel
4. `15_SLOTS.md` — seven legal AI slots (six teacher, one student)
5. `20_TEACHER_MODEL.md` — Teacher Model (first-class)
6. `30_STUDENT_MODEL.md` — Student Model (first-class; instructional invariants live here)
7. Rest as needed: packets, surfaces, IIP map, ledger, ISO-GEN, diagnosis, dark layers, strings, failure modes

**Running philosophy (one sentence).** The corpus is the product — retrieve, typeset, score, and lookup are deterministic, and AI runs only where no lookup can exist, against a capped packet, returning output that is CANDIDATE until a human ratifies it.

Public UI says **AI**. Never a vendor name or model slug.

Frozen exam.v1, ISO-GEN L20, live V15, and the public NCERT map sha are not rewritten.
