## A. Verdict on the current constructor

`tools/lbs_construct.py` cannot be the compiler. `unique_diff → guessed mx_type → template` does not establish the curriculum grain, identify a cited mechanism step, license the diagnosis, prove simplification, or prevent answer disclosure. Its 21,124/21,124 census measures JSON coverage, not LBS validity. Keep it only as a legacy artifact to audit; remove it from the production fallback chain. The replacement must sometimes produce **no hint**, with a machine-readable `ProofGap`. A missing hint is preferable to a wrapper, an option reprint, or an unsupported diagnosis.

---

## B. Architecture diagram

```text
READ-ONLY OWNED INTELLIGENCE
  packed ttwin.question.v1          curriculum + enrichment
  data/projection.json              Mx V2 + ISO-GEN/LBS protocols
  existing exact family/rung metadata, where present
               │
               ▼
  [1] Snapshot + element citation catalog
      file hashes, JSON pointers, element hashes, protocol versions
               │
               ▼
  [2] Exact indexes + approved grain bindings
      five-click tags → projection → eligible NCERT units
      typed task recognition narrows an already licensed candidate set
               │
               ▼
  [3] Deterministic recipe-spec compiler
      step + failure route + lower-rung question + grounding + validators
      retrieval first; otherwise fully specified tutorial_bridge queue
               │
       ┌───────┴───────────────────────────┐
       │ Default: deterministic renderer │
       │ Optional: bounded SURFACE slot  │
       │ on locked unit-level packets    │
       └───────┬───────────────────────────┘
               ▼
  [4] Verified, approved, content-addressed unlock_recipe.v1 library
      recipe proofs + rule registry + fixture results
               │
               │ packed item P, wrong letter L
               ▼
  [5] Deterministic instantiator
      JOIN_UNIT → MATCH_MX → SELECT_RECIPE → INSTANTIATE
      → PROJECT_LEARNER → QUALITY_GATE
               │
       ┌───────┴─────────┐
       ▼                 ▼
  PROVED                GAP / REJECTED
  overlay entry         teacher-side diagnostic; no fallback hint
  hint_proof.v1
       │
       ▼
  [6] join_lbs.py, pack time only
      preserve-uids checked before writes
      source freeze unchanged; write a new pack artifact
       │
       ▼
  EXISTING RUNTIME
      wrong letter → followup lookup → submit hint
      → why for hint + return to original, selection cleared
      no model; no original credit; no mastery assertion
```

### Trust boundaries

1. **Source truth:** hash-bound curriculum, enrichment, packed fields and projection elements.
2. **Inference:** a finite registry of reviewed, deterministic rules.
3. **Surface:** wording that cannot change the locked semantic specification.
4. **Release:** independent checks plus an owner-approved electrochemistry sample.

Hashes prove identity, not pedagogy. The proof verifier must also execute the named rules and check their conclusions.

`gold`, register information and design DNA can select fixtures or priorities. They cannot discharge scientific or pedagogical proof obligations.

---

## C. Joins: exact fields and fail-closed rules

### C1. Snapshot and source identities

Create a build-local snapshot catalog without modifying the source files:

```text
source_id → {
    relative_path,
    file_sha256,
    schema_id,
    snapshot_id
}
```

A citation identifies:

```text
(source_id, file_sha256, JSON_pointer, sha256(canonical_JSON(element)))
```

Use RFC 8785 canonical JSON for JSON values. Include a pinned canonicalizer version in the build manifest.

For Markdown protocols, snapshot an indexed section representation with a deterministic source-offset mapping. Cite the indexed element and bind it to the original file hash.

All source references are resolved locally through the catalog. Do not permit arbitrary URLs or file paths supplied by a recipe.

### C2. Packed item identity and tags

Normalize into a compiler view:

```python
PackedIdentity(
    item_uid=packed["uid"],            # not derived from tags
    pack=packed["pack"],
    subject=packed["subject"],
    node=canonical_node(...),
    chapter_id=packed["chapter_id"],
    subtopic_id=packed["subtopic_id"],
)
```

Rules:

- `item_uid` is the overlay identity.
- Retain the packed five-click tags.
- Resolve `node` versus `big_idea_id` using an explicit adapter for the actual packed schema.
- If both exist and disagree after approved normalization: `TAG_CONFLICT`.
- Normalize `chem:C5/H-REDOX` to `C5/H-REDOX` only through a checked, versioned alias table.
- Do not infer chapter or subtopic from `item_uid`.
- Missing or invalid `mcq_key`: no wrong-letter compilation.
- Requested letter equal to `mcq_key`: reject as `NOT_WRONG_LETTER`.

The key is available to the private verifier, not to a recipe author packet.

### C3. Compiled indexes

Use SQLite or immutable JSON indexes. No vector index is needed.

```text
units_by_id[unit_id]
units_by_node_band[(node, grade_band)]
enrichment_by_unit[unit_id]
mx_by_unit_id[(unit_id, mx_id)]
steps_by_unit_id[(unit_id, step_id)]

grain_bindings[
  (pack, subject, node, chapter_id, subtopic_id)
]

recipes_by_route[
  (unit_id, anchor_step_id, route_kind, route_id)
]

unlock_pool_by_failure[(family_id, failure_path_id, rung)]
unlock_pool_by_construct[(construct_id, rung)]
```

Enrichment join:

```python
for enrichment_item in enrichment:
    for unit_id in enrichment_item["serves"]:
        assert unit_id in units_by_id
        enrichment_by_unit[unit_id].append(enrichment_item)
```

The test is exact `unit_id ∈ serves`. Matching nodes alone does not establish service to a unit.

### C4. Cambridge → NCERT grain binding

Do **not** assume the internal record layouts of `projection.json`. Add a strict adapter for its actual `ncert`, `cambridge`, `ncert_by_node_band` and `grain` structures. The adapter emits this compiler-owned view:

```json
{
  "binding_id": "grain-binding:...",
  "tags": {
    "pack": "senior_11_12_as_a",
    "subject": "<exact packed subject value>",
    "node": "C5/H-REDOX",
    "chapter_id": "cam:9701:6",
    "subtopic_id": "AS_A:9701.6.1"
  },
  "candidates": [
    {
      "unit_id": "<an actual NCERT unit_id>",
      "construct_id": "<registered construct>",
      "task_guard_id": "<registered typed predicate>",
      "evidence_step_ids": ["projection-leaf", "unit-scope-leaf"]
    }
  ]
}
```

A `construct_id` is a compiler symbol bound to cited `decision_hinge` and mechanism elements. It is not a model-created ontology.

Candidate computation:

```text
exact Cambridge projection candidates
  ∩ exact node candidates
  ∩ projected pack/grade-band candidates
  ∩ explicit grain candidates
```

Apply only restrictions actually supported by the projection. Missing precision is not replaced with a guessed restriction.

If the existing projection reaches only a hub, it gives a **candidate set**, not a final join. A reviewed grain-binding supplement may record a more precise existing relationship, with citations to both sides. Such supplements are separate, versioned TTwin artifacts; they do not rewrite the maps.

If the relationship itself is absent from owned intelligence, record `MISSING_CAMBRIDGE_GRAIN`. A human may commission an intelligence amendment in a later release. The compiler must not create one implicitly.

### C5. Typed task recognition—not token overlap

Recognizers use narrow grammars and explicit formula/statement parsers. They return a typed task AST, for example:

```text
UniversalClaim(
    property=OxidationStateSign,
    element=Cl,
    domain=Compounds,
    asserted_sign=Negative
)

OxidationStateCalculation(
    species=FormulaAST(...),
    target_element=S,
    supplied_constraints=[...]
)
```

They may **filter an already licensed candidate set** by exact registered `construct_id` and guard results. They cannot introduce a new unit.

For the electrochemistry sample:

| Item content | Necessary distinction |
|---|---|
| Cryolite | A task about electrolyte function is not an oxidation-state calculation merely because a formula appears. Require the full task and a cited function/condition step. |
| FeC₂O₄ | Distinguish compound charge balance, oxalate charge use and any actual coordination question. The formula alone does not license a coordination-entity grain. |
| “Cl in a compound is always negative” | A universal-domain/sign claim; the failure path may use a licensed positive-Cl counterexample and its OS calculation. |
| Sulfur combustion sequence | A named reaction-sequence task; resolve X/Y/Z only through explicit parent information or cited reaction rules, then select the licensed intermediate calculation. |

The supplied information is insufficient to name the actual NCERT unit IDs for these cases. The implementation must discover them from exact projection records and cited guards—or report a gap. It must not print a plausible H-number.

A coordination unit such as H004 is excluded when its registered applicability predicate requires a coordination construct absent from the typed task.

If two candidates remain:

- Retain the candidate set in the proof.
- Resolve only using a cited grain discriminator or approved equivalence binding.
- Otherwise emit `AMBIGUOUS_UNIT`.
- Never choose by token count, array order or “best-looking hinge”.

### C6. Wrong letter → failure route

Create an audited route-binding registry:

```json
{
  "binding_id": "route-binding:...",
  "unit_id": "<exact unit>",
  "anchor_step_id": "<existing nonempty step>",
  "route": {
    "kind": "mx",
    "id": "<existing mx.id>"
  },
  "parent_task_pattern_id": "<registered AST pattern>",
  "wrong_output_pattern_id": "<registered CWO pattern>",
  "anchor_rule_id": "<registered dependency rule>",
  "evidence_step_ids": ["mx-cwo", "mechanism-step", "route-link"]
}
```

`MATCH_MX` means one of:

1. Exact equality of a supported canonical wrong-output AST with a compiled CWO pattern.
2. A registered, replayable specialization of that pattern.
3. An explicitly named, cited `intermediate_omission@step_id` failure route.

It does **not** mean assigning one of seven types from surface similarity.

For a wrong combination or vector, multiple errors may be present. Selection of one anchor must follow a stored failure-path ordering. For q18 B, choosing the X/SO₂ calculation rather than the Y component requires such an ordering; `unique_diff` does not establish it.

If no route matches: `MISSING_MX_MATCH`. If several incompatible routes match without a licensed priority: `AMBIGUOUS_FAILURE_ROUTE`.

`CANDIDATE` Mx remains `CANDIDATE`. An owner-approved pilot can accept a candidate route as a remediation hypothesis if the protocol permits it, but cannot relabel it `VALIDATED`. The theorem establishes **route applicability to the selected output**, not certainty about the student’s mental state.

### C7. Unlock pool selection

Apply the normative order using exact metadata:

1. Existing eligible unlock item with matching family and failure path at a lower rung.
2. Existing eligible unlock item with matching construct at `rung - 1`.
3. Otherwise create a **tutorial_bridge specification queue entry**, using an approved ISO-GEN operator.

No embeddings. No model supplies missing family, rung, construct or failure-path metadata.

A bridge enters the surface-authoring queue only after its gate, grounding, answer program, format, remediation and simplification witness are complete. “Thin pool” does not mean “ask the model to invent a simpler question.”

---

## D. `unlock_recipe.v1` JSON schema

This is the complete library record assembled by the compiler. The model never owns `spec`.

Registered IDs below resolve against a hash-pinned registry. Unknown IDs fail validation. JSON Schema validates shape; the semantic checks following it are also mandatory.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "unlock_recipe.v1.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "recipe_id", "spec_sha256", "spec",
    "surface", "evidence", "field_support"
  ],
  "properties": {
    "schema": { "const": "unlock_recipe.v1" },
    "recipe_id": { "type": "string", "minLength": 1 },
    "spec_sha256": { "$ref": "#/$defs/hash" },
    "spec": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "unit_id", "anchor_step_id", "route", "construct_id",
        "gate_kind", "format", "rung", "origin", "parameters",
        "programs", "alternatives", "required_evidence_roles"
      ],
      "properties": {
        "unit_id": { "type": "string", "minLength": 1 },
        "anchor_step_id": { "type": "string", "minLength": 1 },
        "route": {
          "type": "object",
          "additionalProperties": false,
          "required": ["kind", "id"],
          "properties": {
            "kind": { "enum": ["mx", "intermediate_omission"] },
            "id": { "type": "string", "minLength": 1 },
            "mx_type": {
              "enum": [
                "term_substitution", "condition_omission",
                "relationship_reversal", "scope_error",
                "surface_feature_capture", "mechanism_conflation",
                "operation_confusion"
              ]
            },
            "source_status": { "enum": ["CANDIDATE", "VALIDATED"] }
          },
          "allOf": [
            {
              "if": { "properties": { "kind": { "const": "mx" } } },
              "then": { "required": ["mx_type", "source_status"] }
            }
          ]
        },
        "construct_id": { "type": "string", "minLength": 1 },
        "gate_kind": { "enum": ["move", "fact", "choice"] },
        "format": {
          "enum": [
            "single_mcq", "true_false", "multi_mcq",
            "assertion_reason", "match", "fill_blank"
          ]
        },
        "rung": { "type": "integer", "minimum": 0 },
        "origin": {
          "type": "object",
          "additionalProperties": false,
          "required": ["kind", "source_id"],
          "properties": {
            "kind": {
              "enum": ["retrieved_failure", "retrieved_construct", "tutorial_bridge"]
            },
            "source_id": { "type": "string", "minLength": 1 },
            "operator": {
              "enum": ["SPECIALIZE", "DECOMPOSE_RECOMBINE", "REPARAMETERIZE"]
            }
          }
        },
        "parameters": {
          "type": "object",
          "propertyNames": { "pattern": "^[a-z][a-z0-9_]*$" },
          "additionalProperties": {
            "type": "object",
            "additionalProperties": false,
            "required": ["type", "source", "binder_rule_id", "constraint_rule_ids"],
            "properties": {
              "type": {
                "enum": [
                  "formula", "species", "element", "integer",
                  "rational", "ion", "statement_id", "grounded_atom"
                ]
              },
              "source": {
                "enum": ["parent_task", "parent_wrong", "grounded_leaf"]
              },
              "binder_rule_id": { "type": "string", "minLength": 1 },
              "constraint_rule_ids": {
                "type": "array",
                "items": { "type": "string" },
                "uniqueItems": true
              }
            }
          }
        },
        "programs": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "applicability", "question", "answer", "tell",
            "why", "simpler", "non_disclosure"
          ],
          "properties": {
            "applicability": { "type": "string" },
            "question": { "type": "string" },
            "answer": { "type": "string" },
            "tell": { "type": ["string", "null"] },
            "why": { "type": "string" },
            "simpler": { "type": "string" },
            "non_disclosure": { "type": "string" }
          }
        },
        "alternatives": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["id", "kind", "value_program_id", "license_step_ids"],
            "properties": {
              "id": { "type": "string" },
              "kind": { "enum": ["correct", "distractor"] },
              "value_program_id": { "type": "string" },
              "license_step_ids": {
                "type": "array",
                "minItems": 1,
                "items": { "type": "string" },
                "uniqueItems": true
              }
            }
          }
        },
        "required_evidence_roles": {
          "type": "array",
          "minItems": 1,
          "items": {
            "enum": [
              "hinge", "law", "boundary", "step", "failure",
              "grain", "unlock_source", "grounding", "remediation"
            ]
          },
          "uniqueItems": true
        }
      }
    },
    "surface": {
      "type": "object",
      "additionalProperties": false,
      "required": ["tell", "stem", "options", "why"],
      "properties": {
        "tell": { "$ref": "#/$defs/text" },
        "stem": {
          "allOf": [
            { "$ref": "#/$defs/text" },
            { "minItems": 1 }
          ]
        },
        "options": {
          "type": "object",
          "additionalProperties": { "$ref": "#/$defs/text" }
        },
        "why": {
          "allOf": [
            { "$ref": "#/$defs/text" },
            { "minItems": 1 }
          ]
        }
      }
    },
    "evidence": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "hint_proof.v1.schema.json#/$defs/ProofStep"
      }
    },
    "field_support": {
      "type": "object",
      "minProperties": 1,
      "propertyNames": { "pattern": "^/" },
      "additionalProperties": {
        "type": "array",
        "minItems": 1,
        "items": { "type": "string" },
        "uniqueItems": true
      }
    }
  },
  "$defs": {
    "hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
    "text": {
      "type": "array",
      "items": {
        "oneOf": [
          {
            "type": "object",
            "additionalProperties": false,
            "required": ["phrase_id"],
            "properties": {
              "phrase_id": { "type": "string", "minLength": 1 }
            }
          },
          {
            "type": "object",
            "additionalProperties": false,
            "required": ["slot"],
            "properties": {
              "slot": { "type": "string", "minLength": 1 }
            }
          }
        ]
      }
    }
  }
}
```

### Mandatory recipe semantics

- `spec_sha256 = SHA256(JCS(spec))`. The library manifest additionally hashes the **whole recipe**, including surface and evidence.
- Every pedagogical spec field must have field-level support. Citing an entire unit is insufficient.
- `anchor_step_id` must resolve to an actual nonempty map mechanism step.
- `field_support` points to named steps in the recipe proof DAG.
- A phrase ID resolves to a reviewed grammar production with a semantic signature. A slot resolves to a typed grounded value.
- There is no arbitrary Python, Jinja expression, natural-language instruction, or `eval` in a recipe.
- For fact/choice gates, `tell` is non-null and the surface contains the grounded tell before the question.
- The question must exercise the next licensed move; telling a fact and asking the student to repeat it does not establish an unlock.
- Each distractor has a failure license. Arbitrary numerical neighbours are prohibited.
- `fill_blank` has no alternatives. Other formats satisfy their format-specific cardinality and answer rules.
- Pilot support may be restricted to `single_mcq` and `fill_blank`. Other runtime-supported formats remain unavailable until their verifiers exist.
- Rung and simplification are supported facts or derived results, not integers chosen by an author.
- Recipe applicability includes chemistry boundary conditions. An oxidation-state rule cannot silently cover peroxides, hydrides or ambiguous mixed-valence cases.
- Thin enrichment fails when a required grounding, unlock or remediation role cannot be discharged. An unrelated caution does not count as an assessment source.

Using grammar productions rather than unchecked prose is deliberate: a second model cannot prove that unrestricted wording added no pedagogy.

---

## E. `hint_proof.v1` JSON schema

This is the **new TTwin wire schema**, not a modification of frozen L20. Its `Citation`, `LeafBy`, `DerivedBy`, `ProofStep` and `ProofGap` map through a tested adapter to the existing Lamport representations. Pin that adapter to the actual frozen schema version; refuse incompatible versions.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "hint_proof.v1.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "item_uid", "wrong_letter", "status", "theorem",
    "snapshot_sha256", "rules_manifest_sha256",
    "recipe_sha256", "followup_sha256",
    "steps", "conclusion_step_id", "gates", "gaps"
  ],
  "properties": {
    "schema": { "const": "hint_proof.v1" },
    "item_uid": { "type": "string", "minLength": 1 },
    "wrong_letter": { "enum": ["A", "B", "C", "D"] },
    "status": { "enum": ["PROVED", "GAP", "REJECTED"] },
    "theorem": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "predicate", "unit_id", "anchor_step_id",
            "route_id", "recipe_id", "task_sha256"
          ],
          "properties": {
            "predicate": { "const": "UNLOCK" },
            "unit_id": { "type": "string" },
            "anchor_step_id": { "type": "string" },
            "route_id": { "type": "string" },
            "recipe_id": { "type": "string" },
            "task_sha256": { "$ref": "#/$defs/hash" }
          }
        }
      ]
    },
    "snapshot_sha256": { "$ref": "#/$defs/hash" },
    "rules_manifest_sha256": { "$ref": "#/$defs/hash" },
    "recipe_sha256": { "$ref": "#/$defs/nullableHash" },
    "followup_sha256": { "$ref": "#/$defs/nullableHash" },
    "steps": {
      "type": "array",
      "items": { "$ref": "#/$defs/ProofStep" }
    },
    "conclusion_step_id": { "type": ["string", "null"] },
    "gates": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["gate_id", "result", "witness_step_ids"],
        "properties": {
          "gate_id": { "type": "string" },
          "result": { "enum": ["PASS", "FAIL", "GAP"] },
          "witness_step_ids": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "gaps": {
      "type": "array",
      "items": { "$ref": "#/$defs/ProofGap" }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "status": { "const": "PROVED" } }
      },
      "then": {
        "properties": {
          "theorem": { "type": "object" },
          "recipe_sha256": { "$ref": "#/$defs/hash" },
          "followup_sha256": { "$ref": "#/$defs/hash" },
          "conclusion_step_id": { "type": "string" },
          "gaps": { "maxItems": 0 }
        }
      }
    }
  ],
  "$defs": {
    "hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
    "nullableHash": {
      "oneOf": [
        { "$ref": "#/$defs/hash" },
        { "type": "null" }
      ]
    },
    "Citation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "source_id", "file_sha256", "json_pointer", "element_sha256"
      ],
      "properties": {
        "source_id": { "type": "string" },
        "file_sha256": { "$ref": "#/$defs/hash" },
        "json_pointer": { "type": "string", "pattern": "^/" },
        "element_sha256": { "$ref": "#/$defs/hash" }
      }
    },
    "LeafBy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "citation"],
      "properties": {
        "kind": { "const": "leaf" },
        "citation": { "$ref": "#/$defs/Citation" }
      }
    },
    "DerivedBy": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "kind", "rule_id", "rule_sha256", "premises",
        "inputs", "execution_sha256"
      ],
      "properties": {
        "kind": { "const": "derived" },
        "rule_id": { "type": "string" },
        "rule_sha256": { "$ref": "#/$defs/hash" },
        "premises": {
          "type": "array",
          "minItems": 1,
          "items": { "type": "string" },
          "uniqueItems": true
        },
        "inputs": { "type": "object" },
        "execution_sha256": { "$ref": "#/$defs/hash" }
      }
    },
    "ProofStep": {
      "type": "object",
      "additionalProperties": false,
      "required": ["step_id", "claim", "by"],
      "properties": {
        "step_id": { "type": "string", "minLength": 1 },
        "claim": {
          "type": "object",
          "additionalProperties": false,
          "required": ["predicate", "args"],
          "properties": {
            "predicate": { "type": "string" },
            "args": { "type": "object" }
          }
        },
        "by": {
          "oneOf": [
            { "$ref": "#/$defs/LeafBy" },
            { "$ref": "#/$defs/DerivedBy" }
          ]
        }
      }
    },
    "ProofGap": {
      "type": "object",
      "additionalProperties": false,
      "required": ["obligation", "code", "evidence_step_ids", "detail"],
      "properties": {
        "obligation": { "type": "string" },
        "code": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" },
        "evidence_step_ids": {
          "type": "array",
          "items": { "type": "string" }
        },
        "detail": { "type": "string" }
      }
    }
  }
}
```

`claim.args` and `DerivedBy.inputs` are further validated by the schema registered for that predicate/rule. They are not an escape hatch for arbitrary assertions.

### Proof replay

For every proof:

1. Verify all file and element hashes.
2. Check unique step IDs and an acyclic dependency graph.
3. Resolve every premise.
4. Validate leaf claims against the cited element.
5. Execute each derived rule with its declared inputs and premises.
6. Compare the computed claim with the stored claim.
7. Recompute:

```text
execution_sha256 =
  SHA256(JCS({
    rule_id,
    rule_sha256,
    rules_manifest_sha256,
    premise_claim_hashes,
    inputs,
    computed_claim
  }))
```

8. Require the final `UNLOCK` conclusion and all mandatory gates to pass.
9. Verify that `followup_sha256` is the exact serialized artifact being joined.

A model-produced “PASS” is not a proof step.

### Obligations

These are compiler obligations, applied **in addition to** the actual normative G0–G6 clauses. Bind each obligation to cited protocol clauses in a versioned gate registry; do not silently redefine the existing gate numbering.

| Obligation | Required witness |
|---|---|
| `O_SOURCE` | Valid element citations, compatible schemas and pinned protocols |
| `O_JOIN` | Exact grain path and a resolved applicable unit |
| `O_ROUTE` | Wrong output matches cited Mx or named intermediate omission |
| `O_STEP` | Existing nonempty mechanism step and licensed anchor |
| `O_SPEC_FIRST` | Locked recipe specification predates surface authoring |
| `O_GROUNDING` | All scientific atoms, conditions, answer and remediation supported |
| `O_SIMPLER` | Proper intermediate-gate task, with a strictly lower certified move cost/rung |
| `O_DIFFERENT` | Hint task is not the parent task with options rearranged |
| `O_DISTRACTORS` | Each distractor follows its cited failure program |
| `O_NO_DISCLOSURE` | No full terminal answer, parent key or equivalent answer-identifying output |
| `O_SURFACE` | Surface realizes the locked AST and contains no unlicensed semantic addition |
| `O_RUNTIME` | Original not credited; hint not progress; retry unaided; no mastery claim |
| `O_RELEASE` | Independent checking and owner-approved scope manifest |

---

## F. Deterministic instantiate algorithm

### F1. Numbered pipeline—no model

1. Load approved library, rule registry, snapshot catalog and scope manifest.
2. Reject an unapproved chapter, pack or subject.
3. Check preserve-uids before proposing any replacement.
4. Validate parent identity, tags, body and key.
5. Parse the parent task and the selected wrong output with registered parsers.
6. Join to candidate units through the exact projection.
7. Apply cited task guards; require a resolved unit.
8. Verify that the unit has usable mechanism steps.
9. Match the wrong output to a licensed failure route.
10. Select the approved recipe using the exact route key and applicability predicates.
11. Bind typed parameters from parent fields or cited grounding leaves.
12. Evaluate boundary conditions and deterministic answer programs.
13. Construct the hint task AST and, where needed, licensed distractors.
14. Prove simplification and distinctness relative to the parent task AST.
15. Render using the approved surface grammar.
16. Project to the existing runtime follow-up format.
17. Run structural, semantic, NEVER-pattern, disclosure and protocol gates.
18. Replay the proof independently.
19. Emit the overlay entry only if proved. Otherwise emit a teacher-side gap/rejection record.

### F2. Pseudocode

```python
def instantiate_letter(parent, letter, ctx):
    proof = ProofBuilder(parent_uid=parent["uid"], wrong_letter=letter)

    try:
        ctx.scope.require(parent)

        if parent["uid"] in ctx.preserve_uids:
            return Preserved(parent["uid"])  # replay separately; no replacement

        p = validate_and_cite_parent(parent, letter, proof, ctx)
        parent_task = parse_parent_task(p, ctx.parsers, proof)
        wrong_output = parse_wrong_output(p, letter, parent_task, proof)

        candidates = join_unit_candidates(p.tags, ctx.indexes, proof)
        unit = resolve_unit(candidates, parent_task, ctx.guards, proof)
        require_existing_steps(unit, proof)

        route = match_failure_route(
            unit, parent_task, wrong_output, ctx.route_bindings, proof
        )
        recipe = select_exact_recipe(unit, route, ctx.library, proof)

        bindings = bind_parameters(recipe, p, parent_task, ctx, proof)
        check_recipe_preconditions(recipe, bindings, ctx, proof)

        hint_task = execute_question_program(recipe, bindings, ctx, proof)
        hint_answer = execute_answer_program(recipe, bindings, ctx, proof)
        alternatives = execute_licensed_alternatives(
            recipe, bindings, hint_answer, ctx, proof
        )

        prove_simpler(parent_task, hint_task, route, ctx, proof)
        prove_different_task(parent_task, hint_task, ctx, proof)

        surface = render_approved_surface(
            recipe, bindings, hint_task, alternatives, ctx, proof
        )
        followup = project_runtime_followup(
            surface=surface,
            answer=hint_answer,
            option_order=stable_option_order(
                recipe_hash=ctx.hash(recipe),
                item_uid=p.item_uid,
                wrong_letter=letter,
                alternatives=alternatives,
            ),
            runtime_contract=ctx.runtime_contract,
        )

        check_surface_and_disclosure(
            parent=p,
            parent_task=parent_task,
            wrong_letter=letter,
            hint_task=hint_task,
            followup=followup,
            recipe=recipe,
            ctx=ctx,
            proof=proof,
        )
        check_followup_ok(followup, ctx.runtime_contract, proof)
        proof.conclude_unlock(unit, route, recipe, hint_task, followup)

        verified = ctx.independent_verifier.replay(proof.finish())
        require(verified.status == "PROVED")
        return ProvenOverlay(followup, verified)

    except ProofFailure as error:
        return NoOverlay(proof.finish_failure(error))
```

No exception handler invokes a model or a legacy constructor.

### F3. Simplification and answer-disclosure checks

Use typed tasks, not string similarity.

A simplification witness establishes:

- the hint exercises an ancestor/intermediate move of the licensed parent solution path;
- the hint removes later synthesis, comparison or combination work;
- its certified move cost is strictly lower;
- any needed facts are supplied when the protocol calls for “tell, then question.”

If existing path/rung metadata is absent, a registered parser may construct a dependency graph using already licensed move rules. It may not invent a pedagogical decomposition. Unsupported task families fail closed.

Non-disclosure has two parts:

1. **Information-flow restriction:** parent `mcq_key`, keyed option and teacher route labels cannot supply learner surface slots. They may be read only by private validation rules.
2. **Task-level restriction:** the hint response or explanation must not equal, encode or select the parent’s complete terminal answer.

Do not ban every numerical overlap. q18 may legitimately ask for S in SO₂, producing a value occurring in a larger parent vector. Reject asking for the entire vector, or a scalar that is itself the parent’s complete requested result.

Also reject:

- original A–D as the follow-up choice set;
- option-letter framing;
- combination-membership assertions masquerading as questions;
- unnamed contextual entities;
- an ungrounded stem such as “Which check is required?”

### F4. Concrete no-call instantiation

Assume the compiled library already contains a proved route for q33 C with:

- the correct joined unit and an existing mechanism step;
- the universal-negative-Cl failure route;
- HClO as a cited, applicable counterexample atom;
- cited H = +1, O = −2 and neutral charge-balance rules;
- a lower-rung OS calculation recipe.

Then:

```text
parent wrong output:
    includes statement 3 in an "always correct" combination

MATCH_MX:
    registered universal-sign failure pattern

SELECT_RECIPE:
    counterexample_OS_calculation, target element Cl

INSTANTIATE:
    named species = HClO
    solve: (+1) + x + (-2) = 0
    x = +1
```

Runtime follow-up, expressed here independently of the exact shipped field names:

```json
{
  "format": "fill_blank",
  "stem": "In HClO, the oxidation number of chlorine is [[Cl]].",
  "answers": { "Cl": ["+1", "1"] },
  "why": "For neutral HClO, (+1) + x + (−2) = 0, so x = +1."
}
```

The runtime adapter must serialize this into the actual existing follow-up contract.

No parent key, parent combination, Mx name or model call appears. If HClO or its required rules are not available in the cited payload, this example is **not emit-able**: `MISSING_GROUNDING`.

---

## G. Bounded LLM compile slot

### G1. Classification

Propose two explicitly approved, non-kernel slots:

- **`T-LBS-RECIPE-SURFACE`**: pack-time compiler slot, restricted subtype of T-AUTHOR.
- **`T-LBS-RECIPE-EXAMINE`**: optional independent recipe-level examiner, restricted subtype of T-SOLVE.

Register them in `harness/15_SLOTS.md` before use. Until approved, the compiler operates with deterministic rendering only.

The kernel and `join_lbs.py` cannot import or invoke these clients.

### G2. Unit-level packet whitelist

One frozen packet per eligible unit per signed compile plan:

```json
{
  "slot": "T-LBS-RECIPE-SURFACE",
  "packet_sha256": "<hash>",
  "unit_id": "<exact unit>",
  "protocol_clause_ids": ["<resolved protocol clauses>"],
  "locked_specs": [
    {
      "recipe_id": "<id>",
      "spec_sha256": "<hash>",
      "spec": "<fully compiled specification>",
      "grounding_atoms": ["<only selected cited atoms>"],
      "allowed_phrase_ids": ["<finite approved productions>"],
      "allowed_slot_sequences": ["<registered grammar IDs>"],
      "fixtures": ["<grounded recipe fixtures; no parent key>"]
    }
  ]
}
```

Excluded:

- raw curriculum or enrichment files;
- the comprehensive NCERT map;
- `resolve_node` dumps;
- arbitrary neighbouring units;
- parent `mcq_key` or keyed option;
- examiner comments not present in source;
- free-form requests to choose a hinge, Mx, step, format or remediation.

The packet contains only the selected evidence projection. Being present elsewhere in the map does not authorize a fact in this packet.

### G3. Output schema

The author returns surface patches, not self-authored pedagogy:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["packet_sha256", "surfaces"],
  "properties": {
    "packet_sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$"
    },
    "surfaces": {
      "type": "array",
      "maxItems": 7,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["recipe_id", "spec_sha256", "surface"],
        "properties": {
          "recipe_id": { "type": "string" },
          "spec_sha256": {
            "type": "string",
            "pattern": "^[a-f0-9]{64}$"
          },
          "surface": {
            "$ref": "unlock_recipe.v1.schema.json#/properties/surface"
          }
        }
      }
    }
  }
}
```

The compiler attaches each accepted patch to the unchanged locked specification and validates the complete `unlock_recipe.v1`.

A request to introduce a new wording production goes to human review for a future phrase-registry version. It cannot pass through an unrestricted string field.

### G4. Prohibited additions

Any added or altered protected field is a `bundle_breaches` failure, including:

- target state;
- misconception or distractor mapping;
- anchor/discrimination point;
- format or DoK;
- figure;
- remediation route;
- elevation pattern or synthesis hinge;
- subject fact outside the selected grounding;
- new chemical example, exception or species not licensed by the packet.

A model cannot “repair” an empty mechanism, select a better unit or assign a lower rung.

### G5. Gates and author/checker separation

Before authoring:

- evidence closure complete;
- grain and route resolved;
- specification hash frozen;
- packet passes whitelist validation;
- budget reservation exists.

After authoring:

- exact schema;
- packet/spec hash agreement;
- no new IDs or slots;
- grammar accepts surface and recovers the same semantic AST;
- all deterministic fixture checks pass;
- independent examiner, if used, is a separate invocation/identity with no author conversation state;
- examiner cannot approve a failed deterministic gate.

Examiner output is a veto/advisory artifact referencing recipe and fixture IDs. It is not a scientific proof leaf. Human approval remains necessary for release.

### G6. Hard call bounds

Make the bounds policy, not an estimate:

- At most **one author packet per unit**.
- At most **one independent examiner packet per unit**.
- At most **seven route variants per packet** for this plan.
- No automatic retries, repair loops or packet splitting.
- Oversized packets or excess variants become queue gaps.
- Every call reserves a unique `(plan_id, unit_id, slot)` ledger entry before dispatch.

The seven-variant limit is a compile-plan cap, **not** a claim that every unit has at most seven Mx records.

**Electrochemistry pilot:**

```text
29 H-REDOX units + 24 H-ECHEM units = at most 53 units
53 author + 53 examiner = at most 106 calls
```

Actual eligibility may be much lower because of steps, grain and enrichment gaps.

**Full chemistry, only after owner expansion approval:**

```text
523 units × 1 author = at most 523 author calls
523 units × 1 examiner = at most 523 examiner calls
total ≤ 1,046 calls per signed library release
```

Deterministic rendering requires **zero** author calls. Instantiating all packed items requires **zero** calls.

Also, `523 × 7 = 3,661`, not “a few hundred.” A few hundred reusable recipes may be an eventual coverage outcome; it must not be asserted as an arithmetic guarantee.

---

## H. Python layout, CLI and overlay integration

### H1. Files to add

```text
/home/harik/TTwin/tools/
  lbs_compile.py                  # snapshot/index/plan/library orchestration
  lbs_instantiate.py              # deterministic pack sweep
  lbs_replay.py                   # independent proof replay and gold replay
  lbs_owner_gate.py               # sample + approval verification

  lbs/
    __init__.py
    canonical.py                 # canonical JSON, hashing
    snapshot.py                  # source catalog, element citations
    source_adapters.py           # actual packed/map/projection schemas
    indexes.py                   # exact indexes
    grain.py                     # candidate joins and grain witnesses
    task_ast.py                  # typed parent/hint tasks
    parsers.py                   # registered narrow recognizers
    chemistry.py                 # formula/charge/OS programs, bounded domains
    routes.py                    # CWO matching and anchored failure routes
    pool.py                      # exact lower-rung retrieval
    specs.py                     # locked recipe specs; bridge queue
    recipes.py                   # validation and library selection
    surface.py                   # approved phrase grammar + rendering
    proof.py                     # proof DAG builder and gaps
    verify.py                    # independent rule replay
    lamport_adapter.py           # frozen L20 schema adapter only
    quality.py                   # AST checks + existing lbs_quality integration
    runtime_adapter.py           # existing follow-up serialization
    overlay.py                   # overlay schema, conflict handling
    owner_gate.py                # signed scope/sample checks
    rules.py                     # registry; no arbitrary dynamic execution
    errors.py

  lbs_ai/
    recipe_surface.py            # explicitly invoked pack-time client
    recipe_examiner.py
    packet.py                    # strict projection and hash
    budget.py                    # signed-plan call ledger

  schemas/
    unlock_recipe.v1.schema.json
    hint_proof.v1.schema.json
    lbs_overlay.v1.schema.json
    lbs_owner_approval.v1.schema.json

  tests/lbs/
    ...
```

Compiler support data:

```text
data/lbs/
  aliases.v1.json
  grain_bindings.v1.json
  route_bindings.v1.json
  phrase_registry.v1.json
  rules_manifest.v1.json
  preserve_uids.v1.json
  never_cases.v1.json
```

These are new, reviewed artifacts. They must not be populated by fuzzy matching and then treated as existing intelligence.

### H2. `tools/lbs_compile.py` sketch

```python
def snapshot_sources(config):
    # Read only supported sources; record schemas and element hashes.
    return build_snapshot(config.source_paths)

def build_indexes(snapshot, adapters):
    units = adapters.read_units(snapshot)
    enrichment = adapters.read_enrichment(snapshot)
    projection = adapters.read_projection(snapshot)
    return ExactIndexes.build(units, enrichment, projection)

def compile_grain_bindings(indexes, approved_bindings, proof_ctx):
    # Existing projection only, plus separately approved cited bindings.
    return grain.compile_exact(indexes, approved_bindings, proof_ctx)

def compile_unit_spec(unit_id, ctx):
    unit = ctx.indexes.units_by_id[unit_id]
    require_nonempty_mechanism_steps(unit)
    routes = compile_cited_routes(unit, ctx)
    specs, gaps = [], []

    for route in routes:
        try:
            source = select_lower_rung_source(route, ctx.pool)
            spec = assemble_locked_spec(unit, route, source, ctx)
            verify_spec_evidence_and_programs(spec, ctx)
            specs.append(spec)
        except ProofFailure as error:
            gaps.append(error.to_gap())

    return specs, gaps

def build_compile_plan(scope, ctx):
    require_scope_authorization(scope, ctx.owner_approval)
    return bounded_unit_plan(
        units=ctx.eligible_units(scope),
        max_variants_per_unit=7,
        author_calls_per_unit=1,
        examiner_calls_per_unit=1,
        retries=0,
    )

def compile_library(plan, ctx, surface_patch_dir=None):
    library, gaps = [], []

    for unit_id in plan.unit_ids:
        try:
            specs, unit_gaps = compile_unit_spec(unit_id, ctx)
            gaps.extend(unit_gaps)

            for spec in specs:
                surface = (
                    load_checked_patch(spec, surface_patch_dir, ctx)
                    if surface_patch_dir
                    else deterministic_surface(spec, ctx.phrases)
                )
                recipe = assemble_recipe(spec, surface)
                run_recipe_fixtures(recipe, ctx)
                ctx.verifier.verify_recipe(recipe)
                library.append(recipe)

        except ProofFailure as error:
            gaps.append(error.to_gap())

    return write_unapproved_library_and_report(library, gaps, ctx)

def main():
    args = parse_args()

    # No AI import or network action anywhere in this control flow.
    ctx = load_read_only_context(args)
    dispatch = {
        "snapshot": command_snapshot,
        "index": command_index,
        "plan": command_plan,
        "library": command_library,
        "verify": command_verify,
    }
    return dispatch[args.command](args, ctx)
```

AI execution is a separate explicit command, never a subroutine called when compilation fails.

### H3. CLI

```bash
python tools/lbs_compile.py snapshot --config config/lbs-electrochem.json
python tools/lbs_compile.py index --snapshot build/lbs/snapshot.json
python tools/lbs_compile.py plan \
  --scope config/lbs-electrochem.json \
  --out build/lbs/compile-plan.json

# Default, no AI:
python tools/lbs_compile.py library \
  --plan build/lbs/compile-plan.json \
  --surface-source deterministic

# Optional, only after slot authorization:
python -m tools.lbs_ai.recipe_surface \
  --plan build/lbs/compile-plan.json \
  --packets build/lbs/packets \
  --out build/lbs/surface-patches

python tools/lbs_instantiate.py \
  --scope config/lbs-electrochem.json \
  --library build/lbs/library.json \
  --preserve data/lbs/preserve_uids.v1.json \
  --out build/lbs/candidate-overlay.json

python tools/lbs_replay.py \
  --overlay build/lbs/candidate-overlay.json \
  --proofs build/lbs/proofs \
  --fixtures data/lbs/fixtures

python tools/lbs_owner_gate.py make-sample \
  --overlay build/lbs/candidate-overlay.json \
  --out build/lbs/owner-sample

python tools/lbs_owner_gate.py verify \
  --approval build/lbs/owner-approval.json
```

### H4. Overlay schema

Use a compiler interchange artifact with exact nested destination paths:

```text
lbs_overlay.v1
  schema: const "lbs_overlay.v1"
  snapshot_sha256: Hash
  library_sha256: Hash
  scope_sha256: Hash
### H4. Overlay schema and `join_lbs.py` integration

The overlay is a **pack-time interchange artifact**, not a replacement exam file. Proof references remain teacher-side. Only the validated `followup` value is copied into:

```text
assessment.learn_by_solve.wrong[letter].followup
```

Use this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "lbs_overlay.v1.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema",
    "snapshot_sha256",
    "library_sha256",
    "scope_sha256",
    "preserve_manifest_sha256",
    "records"
  ],
  "properties": {
    "schema": { "const": "lbs_overlay.v1" },
    "snapshot_sha256": { "$ref": "#/$defs/hash" },
    "library_sha256": { "$ref": "#/$defs/hash" },
    "scope_sha256": { "$ref": "#/$defs/hash" },
    "preserve_manifest_sha256": { "$ref": "#/$defs/hash" },
    "records": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "item_uid",
          "parent_sha256",
          "tags",
          "assessment",
          "proofs"
        ],
        "properties": {
          "item_uid": { "type": "string", "minLength": 1 },
          "parent_sha256": { "$ref": "#/$defs/hash" },
          "tags": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "pack", "subject", "node", "chapter_id", "subtopic_id"
            ],
            "properties": {
              "pack": { "type": "string" },
              "subject": { "type": "string" },
              "node": { "type": "string" },
              "chapter_id": { "type": "string" },
              "subtopic_id": { "type": "string" }
            }
          },
          "assessment": {
            "type": "object",
            "additionalProperties": false,
            "required": ["learn_by_solve"],
            "properties": {
              "learn_by_solve": {
                "type": "object",
                "additionalProperties": false,
                "required": ["wrong"],
                "properties": {
                  "wrong": {
                    "type": "object",
                    "minProperties": 1,
                    "maxProperties": 3,
                    "propertyNames": { "enum": ["A", "B", "C", "D"] },
                    "additionalProperties": {
                      "type": "object",
                      "additionalProperties": false,
                      "required": ["followup"],
                      "properties": {
                        "followup": {
                          "$ref": "runtime_followup.schema.json"
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "proofs": {
            "type": "object",
            "minProperties": 1,
            "maxProperties": 3,
            "propertyNames": { "enum": ["A", "B", "C", "D"] },
            "additionalProperties": { "$ref": "#/$defs/hash" }
          }
        }
      }
    }
  },
  "$defs": {
    "hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$"
    }
  }
}
```

`runtime_followup.schema.json` must describe the **actual shipped follow-up contract**, verified against the existing parser and `followup_ok`. It is a pinned local dependency, not a permissive placeholder. Compilation stops if that contract has not been established.

Each proof hash resolves through the local content-addressed store:

```text
build/lbs/proofs/<hint_proof_sha256>.json
```

No recipe-supplied filesystem paths are followed.

#### Cross-field validation

JSON Schema is insufficient for these checks; implement them in `lbs/overlay.py`:

```python
def validate_overlay_record(record, parent, ctx):
    require(record["item_uid"] == parent["uid"])
    require(record["parent_sha256"] == hash_canonical(parent))
    require(record["tags"] == compiler_tag_view(parent, ctx.aliases))
    require(record["item_uid"] not in ctx.preserve_uids)

    wrong = record["assessment"]["learn_by_solve"]["wrong"]
    require(set(wrong) == set(record["proofs"]))
    require(parent["assessment"]["mcq_key"] not in wrong)

    for letter, entry in wrong.items():
        proof = ctx.proofs.load_verified_hash(record["proofs"][letter])
        require(proof["status"] == "PROVED")
        require(proof["item_uid"] == record["item_uid"])
        require(proof["wrong_letter"] == letter)
        require(proof["followup_sha256"] == hash_canonical(entry["followup"]))
        ctx.verifier.replay(proof)
```

Use the packed-schema adapter for the actual key location; the pseudocode does not authorize assuming a field layout different from the source.

Additional requirements:

- Unique `item_uid` across records.
- Scope, snapshot and library hashes agree with the release manifest.
- Every emitted wrong-letter entry has exactly one proved artifact.
- Gap and rejection reports are separate files, never learner follow-ups.
- A keyed parent may have zero, one, two or three compiled hints. Coverage is reported honestly.
- Tags are validated but never rewritten by the join.

#### Pack-time join

Extend `join_lbs.py` with a proof-overlay mode:

```bash
python tools/join_lbs.py \
  --base-pack <existing-pack-input> \
  --proof-overlay build/lbs/candidate-overlay.json \
  --owner-approval build/lbs/owner-approval.json \
  --out build/packs/electrochem-owner-approved/
```

Control flow:

1. Verify the approval and all bound artifact hashes.
2. Verify source files and destination are distinct; refuse in-place writes.
3. Verify every new overlay proof.
4. Load preserved overlays from their hash-pinned preserve manifest.
5. Reject any compiler record targeting a preserved UID.
6. Reject duplicate or conflicting overlay authorities.
7. Copy only approved follow-ups into a newly assembled pack.
8. Validate the assembled pack and replay the browser contract tests.
9. Write to a temporary destination, then publish atomically.
10. Verify source hashes remain unchanged.

Do not inherit unapproved legacy hints for non-preserved items. In particular, “no compiled hint” must not fall back to `lbs_construct.py`, an old F3 follow-up, or a generic wrapper.

Preserved gold overlays remain unchanged and are tracked separately from new proof-covered entries. Preservation is **not** proof certification. If a preserved artifact cannot yet be replayed, report it as `PRESERVED_UNREPLAYED`; do not fabricate a proof or include it in compiled coverage. If a preserved artifact conflicts with a mandatory NEVER/security gate, block the release for owner resolution rather than silently replacing it.

---

## I. Tests

Use three layers:

1. **Unit and property tests:** synthetic fixtures explicitly identified as test-only.
2. **Repository integration tests:** citations resolve against actual snapshotted intelligence.
3. **Packed/browser tests:** inspect what the learner receives and how the existing runtime behaves.

A synthetic fixture cannot establish production proof coverage.

### I1. Join and evidence tests

| Test | Required result |
|---|---|
| Exact `unit_id ∈ serves` | Enrichment joins only to listed units |
| Node-only enrichment match | Rejected as insufficient evidence |
| Cambridge tags without usable grain | `MISSING_CAMBRIDGE_GRAIN`; no overlay |
| Two applicable unit candidates without discriminator | `AMBIGUOUS_UNIT` |
| Token-overlap “winner” contradicts typed task | Never selected |
| Empty `mechanism.steps` | `EMPTY_MECHANISM_STEPS` |
| Route references nonexistent step | `MISSING_ANCHOR_STEP` |
| Wrong-output AST has no licensed route | `MISSING_MX_MATCH` |
| Required enrichment role missing | `THIN_ENRICHMENT` |
| Citation element changed | Proof replay fails |
| Rule implementation hash changed | Proof invalidated pending recompilation |
| `CANDIDATE` Mx used | Status retained; never promoted automatically |

Add an adversarial grain fixture in which a coordination unit shares more stem words than the correct candidate. Changing the token overlap must have **no effect** on the exact join.

### I2. S1: preserve and replay q1

UID:

```text
9701_m16_qp_12:q1
```

Tests:

- Compiler sweep produces no replacement record for this UID.
- Pack join preserves the existing owner-approved follow-ups exactly.
- Replay attempts independently establish the following semantic targets:

| Wrong letter | Required hint task |
|---|---|
| B | OS of O and H within a named OH group in Mg(OH)₂ |
| C | OS of S in Na₂SO₄, with grounded givens |
| D | OS of Cl in NH₄Cl |

For each letter, replay checks:

- actual grain and mechanism-step citations;
- cited route applicability;
- named species binding;
- deterministic answer;
- licensed distractors, if present;
- simpler intermediate task;
- no parent choice-set reproduction;
- no disclosure of the correct compound or parent key;
- explanation concerns the hint’s move.

The gold label is a **test expectation**, not evidence. If real intelligence cannot discharge a required obligation, replay returns the specific gap while leaving the preserved asset untouched.

### I3. S3: thinking-prod fixtures

For `9701_m17_qp_12:q33`, C:

```text
Task: oxidation state of Cl in named HClO
Answer: +1
```

For `9701_m18_qp_12:q18`, B:

```text
Task: oxidation state of S in named SO2
Answer: +4
```

Assert:

- Surface contains the named species, not “that species”.
- The response requires a calculation rather than combination membership.
- q33’s HClO is licensed by actual parent/map/enrichment evidence.
- q18’s X/SO₂ selection follows the cited failure-path ordering.
- The parent’s complete answer is not produced.
- Removing the grounding or route-order evidence changes the result to a gap.

These are conditional production success tests: **pass with sufficient actual evidence; otherwise produce the prescribed gap**, not an uncited replacement.

### I4. NEVER F3 as rejection fixtures

Store the exact rejected text in `data/lbs/never_cases.v1.json`, with UID, letter and failure codes.

Required rejection codes include:

```text
OPTION_REPRINT
COMBINATION_MEMBERSHIP_NOT_TASK
UNRESOLVED_ENTITY_REFERENCE
NO_INTERMEDIATE_MOVE
```

Test both:

1. **Exact historical forms:** normalized Unicode, whitespace and punctuation variants.
2. **Semantic variants:** wording changes that preserve the prohibited task structure.

Examples:

- `Option C is "2 and 3 only..."` → reject.
- “The selected combination includes statement 3; does it belong?” → reject even without the exact banned phrase.
- `This option is "X: −2; Y: +4; Z: +6"...` → reject.
- “Calculate the state of that species here” without a resolved named referent → reject.

Use two independent controls:

- historical-pattern denial for known served failures;
- typed-task validation for equivalent failures.

A regex blacklist alone is not sufficient.

### I5. F0, F1 and F2 regression tests

- Reject taxonomy questions such as “What did they drop?”
- Reject wrapper shapes recognized by `lbs_quality.is_wrapper_shape`.
- Reject distractors formed by shuffling the original answer clauses.
- Reject hint responses equivalent to the parent’s complete terminal answer.
- Reject explanation strings such as “The keyed choice is C”.
- Reject Mx type names anywhere in the learner projection.
- Assert choice ordering is deterministic and not universally keyed A.
- Do not require a hint key to differ from the parent key letter; coincidental equality is not disclosure.

### I6. Proof and compiler mutation tests

Starting from a proved fixture, mutate one element at a time:

```text
unit_id
anchor_step_id
mx_id
grounding species
boundary condition
hint answer
distractor program
surface phrase
followup bytes
citation hash
rule hash
premise reference
```

Each mutation must either:

- fail replay; or
- require a newly compiled proof against a valid changed specification.

Also reject cyclic proof graphs, unknown rule IDs, missing premises, duplicate step IDs, unresolved surface slots and stale owner approvals.

### I7. No per-item LLM

Enforce this architecturally and in CI:

```python
def test_instantantiation_has_no_network(monkeypatch, corpus_fixture, ctx):
    monkeypatch.setattr(socket.socket, "connect", fail_network)
    monkeypatch.setattr(socket, "create_connection", fail_network)
    instantiate_pack(corpus_fixture, ctx)
```

Additional tests:

- Compiler/instantiator/kernel dependency graphs cannot import `tools.lbs_ai`.
- Instantiation succeeds without model credentials or SDKs installed.
- Increasing item count does not change AI call count.
- No author packet is scheduled by `(item_uid, wrong_letter)`.
- Call ledger uniqueness enforces `(plan_id, unit_id, slot)`.
- Pilot budget cannot exceed 106 calls.
- Invalid surface output becomes a gap; it does not trigger a retry.
- A missing recipe cannot dispatch an author request during a pack sweep.

Run the deterministic sweep in a network-disabled process. Unit monkeypatches alone are not a sufficient boundary.

### I8. Runtime and immutable-source tests

Browser tests against the shipped runtime must verify:

1. Wrong letter selects its exact overlay follow-up.
2. Hint submission returns to the original.
3. Original selection is cleared.
4. Only the hint’s explanation appears.
5. Hint completion does not credit the original or increase progress.
6. A subsequent answer is recorded as an assisted original attempt where applicable, not isomorphic mastery.
7. No I18 family-mastery claim is emitted.
8. Missing follow-up does not expose a legacy fallback.

Before/after hashes must prove no changes to frozen exam sources, live V15 or `/home/harik/raw/LamportEngine`.

---

## J. Rollout: electrochemistry only, owner gate before expansion

### J1. Scope lock

The initial release manifest permits only:

```text
pack: senior_11_12_as_a
chapter_id: cam:9701:6
nodes: chem:C5/H-REDOX, chem:C5/H-ECHEM
subject: exact packed chemistry value
```

Check subtopics against the approved projection bindings, including the supplied `AS_A:9701.6.1` and `AS_A:9701.24.1` cases.

Do not infer that chapter/subtopic numbering is interchangeable. Conflicts require inspection, not normalization by guess.

The reported “approximately 213 keyed items” is an expectation to audit, not an asserted denominator. Publish actual counts for:

```text
eligible keyed parents
eligible wrong letters
preserved letters
newly proved letters
gapped letters by code
rejected letters by code
```

Do not use structural completeness as the release criterion.

### J2. Required owner sample

Create a real packed sample, not a spreadsheet of stems.

Include:

| Sample | Owner checks |
|---|---|
| `9701_m16_qp_12:q1`, B/C/D | Preserved byte identity; named intermediate tasks; replay status |
| `9701_m17_qp_12:q33`, C | HClO calculation, not statement-combination restatement |
| `9701_m18_qp_12:q18`, B | Named SO₂ calculation and justified anchor selection |
| Cryolite q3 | Correct task construct and grain; no formula-only misclassification |
| FeC₂O₄ q10 | Correct compound/charge/coordination distinction; cited boundary conditions |

The full UIDs for cryolite q3 and FeC₂O₄ q10 were not supplied. Resolve them from the packed corpus and require the owner sample manifest to record the exact UIDs and parent hashes. Do not invent their paper/session identifiers.

Also include:

- at least one example per emitted recipe/route variant;
- all ambiguity resolutions;
- all candidate-Mx routes proposed for pilot use;
- representative gaps, showing that no wrapper was substituted.

For each sample letter, present:

1. Original learner view.
2. Clicked wrong letter.
3. Actual hint learner view.
4. Hint answer and explanation in teacher view.
5. Joined unit and projection path.
6. Mechanism step and route evidence.
7. Simplification and disclosure witnesses.
8. Proof replay result.

### J3. Approval artifact

`lbs_owner_approval.v1` must bind at least:

```json
{
  "schema": "lbs_owner_approval.v1",
  "decision": "APPROVE_PILOT",
  "scope_sha256": "<hash>",
  "snapshot_sha256": "<hash>",
  "library_sha256": "<hash>",
  "overlay_sha256": "<hash>",
  "packed_sample_sha256": "<hash>",
  "sample_manifest_sha256": "<hash>",
  "preserve_manifest_sha256": "<hash>",
  "reviewer_id": "<owner identity>",
  "reviewed_at": "<timestamp>",
  "reviewed_cases": ["<exact item_uid + letter identifiers>"],
  "allow_scope_expansion": false,
  "signature": "<verified signature>"
}
```

The approval is external to the overlay to avoid circular hashing. Use a signature verified against the configured owner key, not merely a typed name.

Release gate:

```python
require(all_new_entries_proved)
require(all_mandatory_tests_pass)
require(approval.signature_valid)
require(approval.hashes_match_current_artifacts)
require(required_owner_cases_reviewed)
require(current_scope == approval.approved_scope)
require(preserved_assets_unchanged)
require(no_unapproved_legacy_fallbacks)
```

Any artifact change invalidates its bound approval.

Owner approval cannot waive an empty step, invalid citation, NEVER shape or failed disclosure gate. Such failures require corrected inputs and recompilation.

### J4. Expansion

No automatic chapter expansion after a green CI run.

Expansion requires a separate owner decision naming the next scope. The electrochemistry approval must explicitly **not** authorize all chemistry, physics or biology.

Indexing existing chemistry metadata is not permission to emit hints outside the pilot. The chemistry-tagged 9,472 items remain intact; their tags are not rewritten to improve coverage.

---

## K. Honest gaps

| Gap | Compiler behavior | Permitted resolution |
|---|---|---|
| Empty `mechanism.steps` | Skip all affected routes; `EMPTY_MECHANISM_STEPS` | Separately governed intelligence amendment, then recompile |
| Missing precise Cambridge↔NCERT grain | Retain candidate set; no final join | Cited, reviewed grain binding or upstream intelligence amendment |
| Thin enrichment | Skip recipes whose required roles lack evidence | Add owned, cited grounding/probe/remediation evidence |
| No exact Mx match | `MISSING_MX_MATCH` | Establish a cited route; never assign a type from resemblance |
| Unanchored intermediate omission | Reject the proposed fallback | Supply an explicit failure-path-to-step link |
| Multiple route matches | `AMBIGUOUS_FAILURE_ROUTE` | Cited selection priority or reviewed route equivalence |
| Unresolved species or X/Y/Z | No instantiation | Explicit parent evidence or a licensed reaction-resolution rule |
| Unsupported formula/task grammar | `UNSUPPORTED_TASK_GRAMMAR` | Extend and test a bounded parser/program |
| Missing lower-rung/path evidence | Cannot prove “simpler” | Establish the path/rung or a licensed dependency-graph witness |
| Empty unlock pool | Queue a tutorial-bridge specification | Complete the specification before any surface slot |
| Unlicensed distractor | Reject that recipe/variant | Supply a failure license; do not generate random alternatives |
| Gold cannot replay | Preserve unchanged, report unproved status | Fill real evidence gaps; gold status is not a citation |
| Unknown runtime schema | Stop overlay emission | Establish and pin the actual shipped contract |
| Physics/biology Mx empty | No chemistry-style fabrication | Separate intelligence work and separate scope approval |

Two limits must remain explicit:

- The compiler proves a supported **remediation route for an observable wrong output**, not the student’s private cognitive cause.
- It proves only within supported task grammars and reviewed inference rules. It does not claim a general semantic proof of arbitrary natural-language hints.

**Release principle:** every newly emitted follow-up carries a replayable proof; every unresolved obligation yields no new follow-up. Coverage is earned by stronger owned intelligence and verified reuse—not by a fallback model call.