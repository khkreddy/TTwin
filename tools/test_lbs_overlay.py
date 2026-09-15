#!/usr/bin/env python3
"""Drive the real pack-time constructor/joiner. Fail stamp banks."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from join_lbs import census_item, join_items  # noqa: E402
from lbs_construct import (  # noqa: E402
    LETTERS,
    construct_lbs,
    ensure_item,
    is_stamp_lbs,
    lbs_complete,
)
from lbs_quality import lbs_relevant  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lbs_item.json"
NUMERIC = Path(__file__).resolve().parent / "fixtures" / "lbs_numeric.json"
STAMP_SOLVE = "The keyed choice is"
STAMP_STEMS = (
    "What did they drop?",
    "Which description of that error",
    "What kind of boundary error",
    "Which description fits?",
    "Which claim does the item actually require?",
    "Which value is required?",
    "A working that is consistent with this item gives",
    "A student answered as if a different condition held",
    "Which check is required?",
    "Which rule is required?",
    "The stem names a specific species or process",
    "A word or symbol in the stem is easy to spot",
    "A student obtained a different numerical value from the working this item requires",
)


def _assert_quality(lbs: dict, item: dict, packed: bool = False) -> list[str]:
    assert STAMP_SOLVE not in (lbs.get("solve") or ""), lbs.get("solve")
    assert "Required:" in (lbs.get("solve") or "")
    fu_keys = []
    for L, row in (lbs.get("wrong") or {}).items():
        fu = row["followup"]
        stem = fu.get("stem") or ""
        for p in STAMP_STEMS:
            assert p not in stem, (L, p, stem[:120])
        blob = " ".join((fu.get("options") or {}).values())
        assert "A stated condition that still applies" not in blob
        assert "A directed relation (cause/effect" not in blob
        assert fu.get("key") in LETTERS
        assert "mx_type" not in stem
        fu_keys.append(fu["key"])
        key_txt = str((item.get("options") or {}).get(item["assessment"]["mcq_key"]) or "").strip()
        if looks_num(key_txt):
            assert key_txt not in stem, (L, "key leaked in follow-up stem", stem)
            assert key_txt not in blob, (L, "key leaked in follow-up options", blob)
    return fu_keys


def looks_num(s: str) -> bool:
    return bool(s) and any(ch.isdigit() for ch in s) and len(s) <= 24


def test_join_fixture() -> dict:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    n, stats = join_items([item])
    a = item["assessment"]
    lbs = a["learn_by_solve"]
    key = a["mcq_key"]
    expect = set(LETTERS) - {key}
    assert n == 1
    assert lbs_complete(lbs, key, item.get("options") or {}, item)
    assert lbs_relevant(item, lbs, key)
    assert set(lbs["wrong"]) == expect
    assert not is_stamp_lbs(lbs)
    _assert_quality(lbs, item)
    seeds = a.get("modify_seeds") or []
    assert len(seeds) == len(expect)
    for s in seeds:
        ins = s["instruction"]
        assert "student who still Student" not in ins
        assert ins.startswith("Rewrite this item so option ")
    assert (a.get("examiner_comment") or {}).get("present") is False
    c = census_item(item)
    assert c["keyed"] and c["lbs_complete"] and c["lbs_relevant"] and c["modify_seeds"]
    return {"item": item, "stats": stats}


def test_replaces_stamps() -> None:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    item["assessment"]["learn_by_solve"] = {
        "solve": "The keyed choice is C: colour spreads faster in hot water.",
        "wrong": {
            "A": {
                "mx_type": "condition_omission",
                "pathway": "Student dropped a condition.",
                "followup": {
                    "stem": "What did they drop?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
            "B": {
                "mx_type": "condition_omission",
                "pathway": "Student dropped a condition.",
                "followup": {
                    "stem": "What did they drop?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
            "D": {
                "mx_type": "condition_omission",
                "pathway": "Student dropped a condition.",
                "followup": {
                    "stem": "What did they drop?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
        },
    }
    assert is_stamp_lbs(item["assessment"]["learn_by_solve"])
    assert ensure_item(item) is True
    lbs = item["assessment"]["learn_by_solve"]
    assert not is_stamp_lbs(lbs)
    assert lbs_relevant(item, lbs)
    _assert_quality(lbs, item)


def test_numeric_no_key_leak() -> None:
    item = json.loads(NUMERIC.read_text(encoding="utf-8"))
    lbs = construct_lbs(item)
    assert lbs
    key_txt = item["options"][item["assessment"]["mcq_key"]]
    for L, row in lbs["wrong"].items():
        fu = row["followup"]
        blob = fu["stem"] + " " + " ".join((fu.get("options") or {}).values())
        assert key_txt not in fu["stem"], fu["stem"]
        assert key_txt not in blob, blob
        assert "Which value is required" not in fu["stem"]
        assert "Which check is required" not in fu["stem"]
        assert key_txt[:4] in fu["stem"] or "efficiency" in fu["stem"].lower() or "useful" in blob.lower()
        # each wrong value is named in its own follow-up
        assert str(item["options"][L])[:3] in fu["stem"] or "efficiency" in fu["stem"].lower()


def test_distinct_wrong_letter_followups() -> None:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    lbs = construct_lbs(item)
    stems = {L: lbs["wrong"][L]["followup"]["stem"] for L in lbs["wrong"]}
    assert stems["A"] != stems["B"], stems
    assert "hotter" in stems["A"].lower() or "colder" in stems["A"].lower() or "temperature" in stems["A"].lower()
    assert "particle" in stems["B"].lower() or "move" in stems["B"].lower()


def test_followup_keys_not_always_a() -> None:
    base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    keys = []
    for i, uid in enumerate(
        ["fx:1", "fx:2", "fx:3", "fx:4", "fx:5", "fx:6", "fx:7", "fx:8"]
    ):
        it = json.loads(json.dumps(base))
        it["uid"] = uid
        lbs = construct_lbs(it)
        assert lbs
        keys.extend(row["followup"]["key"] for row in lbs["wrong"].values())
    assert set(keys) - {"A"}, f"all follow-up keys were A: {keys}"


def test_olympiad_parse_or_skip() -> None:
    item = {
        "uid": "jeebench:fixture:q1",
        "stem": (
            "If the team has to include at most one boy, then the number of ways is\n\n"
            "(A) 380\n\n(B) 320\n\n(C) 260\n\n(D) 95"
        ),
        "options": {},
        "assessment": {
            "key_source": "olympiad_gold",
            "key_status": "available",
            "mcq_key": "A",
            "examiner_comment": {"present": False},
        },
    }
    assert ensure_item(item)
    assert item["options"]["A"] == "380"
    lbs = item["assessment"]["learn_by_solve"]
    assert lbs_complete(lbs, "A", item["options"], item)
    assert not is_stamp_lbs(lbs)
    empty = {
        "uid": "jeebench:fixture:empty",
        "stem": "No options printed here.",
        "options": {},
        "assessment": {
            "key_source": "olympiad_gold",
            "key_status": "available",
            "mcq_key": "C",
            "examiner_comment": {"present": False},
        },
    }
    ensure_item(empty)
    assert not empty.get("assessment", {}).get("learn_by_solve")


def test_olympiad_bracket_options() -> None:
    item = {
        "uid": "jeebench:fixture:q38",
        "stem": (
            "Then the triangle $PQR$ has $S$ as its\n\n"
            "[A] centroid\n\n[B] circumcentre\n\n[C] incentre\n\n[D] orthocenter"
        ),
        "options": {},
        "assessment": {
            "key_source": "olympiad_gold",
            "key_status": "available",
            "mcq_key": "D",
            "examiner_comment": {"present": False},
        },
    }
    assert ensure_item(item)
    assert item["options"]["D"] == "orthocenter"
    assert "centroid" not in (item.get("stem") or "")
    lbs = item["assessment"]["learn_by_solve"]
    assert lbs_complete(lbs, "D", item["options"], item)
    assert not is_stamp_lbs(lbs)


def test_preserve_gold_seeds() -> None:
    uid = "fixture:gold-preserve:q1"
    gold_solve = "HClO: H +1, O −2, Cl +1. Two different elements share +1."
    gold_ins = "Rewrite this oxidation-state item so option B remains the trap for two OH groups."
    item = {
        "uid": uid,
        "stem": "Which compound contains two different elements with identical oxidation states?",
        "options": {"A": "HClO", "B": "Mg(OH)₂", "C": "Na₂SO₄", "D": "NH₄Cl"},
        "assessment": {
            "key_source": "cambridge_extract",
            "key_status": "available",
            "mcq_key": "A",
            "examiner_comment": {"present": False},
            "learn_by_solve": {
                "solve": gold_solve,
                "key": "A",
                "wrong": {
                    "B": {
                        "mx_type": "scope_error",
                        "pathway": "two OH groups",
                        "followup": {
                            "stem": "In each OH, what are the oxidation states of O and H?",
                            "options": {"A": "both −1", "B": "O −2 and H +1", "C": "both +1", "D": "O −1 H −1"},
                            "key": "B",
                            "why": "OH is O −2 and H +1",
                        },
                    },
                    "C": {
                        "mx_type": "operation_confusion",
                        "pathway": "sulfur OS",
                        "followup": {
                            "stem": "In Na₂SO₄, what is the oxidation state of S?",
                            "options": {"A": "+2", "B": "+4", "C": "+6", "D": "−2"},
                            "key": "C",
                            "why": "S is +6",
                        },
                    },
                    "D": {
                        "mx_type": "term_substitution",
                        "pathway": "Cl as +1",
                        "followup": {
                            "stem": "What is the oxidation state of chlorine in NH₄Cl?",
                            "options": {"A": "+1", "B": "−1", "C": "+5", "D": "0"},
                            "key": "B",
                            "why": "chloride is −1",
                        },
                    },
                },
            },
            "modify_seeds": [
                {
                    "id": "B:scope_error",
                    "letter": "B",
                    "mx_type": "scope_error",
                    "instruction": gold_ins,
                }
            ],
        },
    }
    assert ensure_item(item) is False or item["assessment"]["learn_by_solve"]["solve"] == gold_solve
    assert item["assessment"]["learn_by_solve"]["solve"] == gold_solve
    assert item["assessment"]["modify_seeds"][0]["instruction"] == gold_ins
    assert "mx_type" not in (item.get("stem") or "")


def test_gold_approved_q1() -> dict:
    """Hari-approved package: follow-ups name Mg(OH)₂ / Na₂SO₄ / NH₄Cl chemistry."""
    packed = ROOT / "data/questions/chemistry-senior.json"
    items = json.loads(packed.read_text(encoding="utf-8"))
    item = next(it for it in items if it.get("uid") == "9701_m16_qp_12:q1")
    a = item["assessment"]
    lbs = a["learn_by_solve"]
    assert a["mcq_key"] == "A"
    assert lbs_relevant(item, lbs, "A")
    assert not is_stamp_lbs(lbs)
    stems = {L: lbs["wrong"][L]["followup"]["stem"] for L in ("B", "C", "D")}
    assert "Mg(OH)" in stems["B"] or "OH" in stems["B"]
    assert "Na" in stems["C"] and ("S" in stems["C"] or "SO" in stems["C"])
    assert "NH" in stems["D"] or "chlorine" in stems["D"].lower() or "Cl" in stems["D"]
    for p in STAMP_STEMS:
        for L, s in stems.items():
            assert p not in s, (L, p, s)
    assert "mx_type" not in (item.get("stem") or "")
    before = json.dumps(lbs, sort_keys=True)
    ensure_item(item)
    after = json.dumps(item["assessment"]["learn_by_solve"], sort_keys=True)
    assert json.loads(before)["wrong"]["B"]["followup"]["stem"] == item["assessment"]["learn_by_solve"]["wrong"]["B"]["followup"]["stem"]
    return {"uid": item["uid"], "stems": stems, "unchanged": before == after}


def test_stamp_fails_relevant() -> None:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    item["assessment"]["learn_by_solve"] = {
        "solve": "The keyed choice is C: colour spreads faster in hot water.",
        "wrong": {
            "A": {
                "mx_type": "condition_omission",
                "pathway": "x",
                "followup": {
                    "stem": "A student answered as if a different condition held. Which check is required?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
            "B": {
                "mx_type": "condition_omission",
                "pathway": "x",
                "followup": {
                    "stem": "Which claim does the item actually require?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
            "D": {
                "mx_type": "condition_omission",
                "pathway": "x",
                "followup": {
                    "stem": "What did they drop?",
                    "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                    "key": "A",
                    "why": "stamp",
                },
            },
        },
    }
    assert is_stamp_lbs(item["assessment"]["learn_by_solve"])
    assert not lbs_relevant(item)


def test_figure_letter_census() -> None:
    item = {
        "uid": "9701_m22_qp_12:q40",
        "stem": "Which diagram shows both a C=O and an O–H group?",
        "options": {"A": "", "B": "", "C": "", "D": ""},
        "options_are_figure": True,
        "figure_src": "data/spectra/originals/9701_m22_qp_12_q40.png",
        "assessment": {
            "key_source": "cambridge_extract",
            "key_status": "available",
            "mcq_key": "B",
            "examiner_comment": {"present": False},
            "learn_by_solve": {
                "solve": "Need both C=O and O–H. Diagram B is the only trace that has both.",
                "key": "B",
                "wrong": {
                    "A": {
                        "mx_type": "condition_omission",
                        "pathway": "omits one of the two groups",
                        "followup": {
                            "stem": "A compound with both C=O and O–H must show which pattern?",
                            "options": {"A": "C=O only", "B": "O–H only", "C": "both", "D": "neither"},
                            "key": "C",
                            "why": "both features",
                        },
                    },
                    "C": {
                        "mx_type": "surface_feature_capture",
                        "pathway": "fingerprint trough",
                        "followup": {
                            "stem": "O–H stretches live at high wavenumber. Which side of the plot?",
                            "options": {"A": "right", "B": "left-hand half", "C": "centre", "D": "never"},
                            "key": "B",
                            "why": "high wavenumber is left",
                        },
                    },
                    "D": {
                        "mx_type": "condition_omission",
                        "pathway": "C=O without O–H",
                        "followup": {
                            "stem": "Which one feature is not enough to claim both groups?",
                            "options": {"A": "canyon plus C=O", "B": "O–H plus C=O", "C": "C=O only", "D": "acid pair"},
                            "key": "C",
                            "why": "C=O alone is not both",
                        },
                    },
                },
            },
            "modify_seeds": [{"id": "A:condition_omission", "letter": "A", "mx_type": "condition_omission"}],
        },
    }
    c = census_item(item)
    assert c["keyed"] and c["eligible"] and c["lbs_complete"]
    assert c["lbs_relevant"] and c["modify_seeds"]
    learner = json.dumps(item.get("stem"))
    assert "mx_type" not in learner
    assert "condition_omission" not in (item.get("stem") or "")


def test_learner_vs_teacher_html(item: dict, out_dir: Path) -> dict:
    payload = out_dir / "lbs_html_item.json"
    payload.write_text(json.dumps(item), encoding="utf-8")
    js = r"""
const fs = require('fs');
const path = process.argv[1];
const item = JSON.parse(fs.readFileSync(path, 'utf8'));
const code = fs.readFileSync('js/paper.js', 'utf8');
const window = global;
eval(code);
if (!global.TTwinPaper) throw new Error('TTwinPaper missing');
const from = Object.keys((item.assessment.learn_by_solve.wrong)||{})[0];
const learner = TTwinPaper.itemHTML(item, 0, {
  interactive: true, showUid: false, teacherTools: false,
  lbsStage: { [item.uid]: { from: from, followup_choice: null, done: false } }
});
const teacher = TTwinPaper.answerKeyHTML({ title: 'key' }, [item]);
if (/mx_type/.test(learner)) throw new Error('learner HTML leaked mx_type');
if (!/term_substitution|condition_omission|relationship_reversal|scope_error|surface_feature_capture|mechanism_conflation|operation_confusion/.test(teacher)) {
  throw new Error('teacher key missing mx type');
}
if (!/Follow-up/.test(teacher) && !/follow-up/i.test(teacher) && !/How to see it/.test(teacher)) {
  throw new Error('teacher key missing LBS solve/follow-up');
}
process.stdout.write(JSON.stringify({ learner_len: learner.length, teacher_len: teacher.length, learner_has_mx: /mx_type/.test(learner), teacher_has_mx_word: true }));
"""
    r = subprocess.run(
        ["node", "-e", js, str(payload)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=20,
    )
    if r.returncode != 0:
        raise SystemExit("node html test failed:\n" + r.stderr + r.stdout)
    return json.loads(r.stdout)


if __name__ == "__main__":
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/dev/stdout")
    html_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp")
    html_dir.mkdir(parents=True, exist_ok=True)
    test_replaces_stamps()
    test_stamp_fails_relevant()
    test_numeric_no_key_leak()
    test_distinct_wrong_letter_followups()
    test_followup_keys_not_always_a()
    test_olympiad_parse_or_skip()
    test_olympiad_bracket_options()
    test_preserve_gold_seeds()
    gold = test_gold_approved_q1()
    test_figure_letter_census()
    result = test_join_fixture()
    html = test_learner_vs_teacher_html(result["item"], html_dir)
    (html_dir / "learner_vs_teacher.html").write_text(
        "<!-- learner mx_type=" + str(html["learner_has_mx"]) + " -->\n"
        + "<!-- teacher_has_mx_word=" + str(html["teacher_has_mx_word"]) + " -->\n"
        + "<!-- solve -->\n" + (result["item"]["assessment"]["learn_by_solve"]["solve"] or "") + "\n",
        encoding="utf-8",
    )
    doc = {
        "ok": True,
        "stats": result["stats"],
        "html": html,
        "solve": result["item"]["assessment"]["learn_by_solve"]["solve"],
        "gold_q1": gold,
    }
    text = json.dumps(doc, indent=2)
    log_path.write_text(text + "\n", encoding="utf-8")
    print(text)
