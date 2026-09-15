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

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lbs_item.json"
STAMP_SOLVE = "The keyed choice is"
STAMP_STEMS = (
    "What did they drop?",
    "Which description of that error",
    "What kind of boundary error",
    "Which description fits?",
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
        # follow-up must mention a fragment of the keyed or wrong option
        ktxt = str((item.get("options") or {}).get(item["assessment"]["mcq_key"]) or "")
        wtxt = str((item.get("options") or {}).get(L) or "")
        joined = stem + " " + blob
        if not packed:
            assert (ktxt[:8] in joined) or (wtxt[:8] in joined) or "required" in joined.lower(), joined[:200]
    return fu_keys


def test_join_fixture() -> dict:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    n, stats = join_items([item])
    a = item["assessment"]
    lbs = a["learn_by_solve"]
    key = a["mcq_key"]
    expect = set(LETTERS) - {key}
    assert n == 1
    assert lbs_complete(lbs, key, item.get("options") or {}, item)
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
    assert c["keyed"] and c["lbs_complete"] and c["modify_seeds"]
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
    _assert_quality(lbs, item)


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
    test_followup_keys_not_always_a()
    test_olympiad_parse_or_skip()
    result = test_join_fixture()
    packed = ROOT / "data/questions/chemistry-igcse.json"
    if packed.is_file():
        items = json.loads(packed.read_text(encoding="utf-8"))
        keyed = [it for it in items if (it.get("assessment") or {}).get("mcq_key") in LETTERS][:80]
        fu_keys = []
        for it in keyed:
            lbs = (it.get("assessment") or {}).get("learn_by_solve")
            assert lbs, it.get("uid")
            assert is_stamp_lbs(lbs) is False, it.get("uid")
            fu_keys.extend(_assert_quality(lbs, it, packed=True))
        assert set(fu_keys) - {"A"}, fu_keys[:12]
    html = test_learner_vs_teacher_html(result["item"], html_dir)
    (html_dir / "learner_vs_teacher.html").write_text(
        "<!-- learner mx_type=" + str(html["learner_has_mx"]) + " -->\n"
        + "<!-- teacher_has_mx_word=" + str(html["teacher_has_mx_word"]) + " -->\n"
        + "<!-- solve -->\n" + (result["item"]["assessment"]["learn_by_solve"]["solve"] or "") + "\n",
        encoding="utf-8",
    )
    doc = {"ok": True, "stats": result["stats"], "html": html, "solve": result["item"]["assessment"]["learn_by_solve"]["solve"]}
    text = json.dumps(doc, indent=2)
    log_path.write_text(text + "\n", encoding="utf-8")
    print(text)
