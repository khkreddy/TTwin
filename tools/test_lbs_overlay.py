#!/usr/bin/env python3
"""Drive the real pack-time joiner on a fixture. Not a reimplementation."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from join_lbs import census_item, join_items  # noqa: E402
from lbs_construct import LETTERS, lbs_complete  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lbs_item.json"


def test_join_fixture() -> dict:
    item = json.loads(FIXTURE.read_text(encoding="utf-8"))
    n, stats = join_items([item])
    a = item["assessment"]
    lbs = a["learn_by_solve"]
    key = a["mcq_key"]
    expect = set(LETTERS) - {key}
    wrong = lbs["wrong"]
    assert n == 1
    assert lbs_complete(lbs, key, item["options"])
    assert set(wrong) == expect
    for L in expect:
        fu = wrong[L]["followup"]
        assert fu.get("stem")
        assert set(fu.get("options") or {}) >= set(LETTERS)
        assert fu.get("key") in LETTERS
        assert wrong[L]["mx_type"]
        assert "mx_type" not in fu["stem"]
        assert "mx_type" not in fu["why"]
    assert a.get("modify_seeds")
    assert len(a["modify_seeds"]) == len(expect)
    assert (a.get("examiner_comment") or {}).get("present") is False
    c = census_item(item)
    assert c["keyed"] and c["lbs_complete"] and c["modify_seeds"]
    return {"item": item, "stats": stats}


def test_learner_vs_teacher_html(item: dict, out_dir: Path) -> None:
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
const learner = TTwinPaper.itemHTML(item, 0, {
  interactive: true, showUid: false, teacherTools: false,
  lbsStage: { [item.uid]: { from: 'A', followup_choice: null, done: false } }
});
const teacher = TTwinPaper.answerKeyHTML({ title: 'key' }, [item]);
if (/mx_type/.test(learner)) throw new Error('learner HTML leaked mx_type');
if (!/term_substitution|condition_omission|relationship_reversal|scope_error|surface_feature_capture|mechanism_conflation|operation_confusion/.test(teacher)) {
  throw new Error('teacher key missing mx type');
}
if (!/Follow-up/.test(teacher) && !/follow-up/i.test(teacher) && !/How to see it/.test(teacher)) {
  throw new Error('teacher key missing LBS solve/follow-up');
}
process.stdout.write(JSON.stringify({ learner_len: learner.length, teacher_len: teacher.length, learner_has_mx: /mx_type/.test(learner), teacher_has_mx_word: /condition_omission|relationship_reversal/.test(teacher) }));
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
    result = test_join_fixture()
    html = test_learner_vs_teacher_html(result["item"], html_dir)
    (html_dir / "learner_vs_teacher.html").write_text(
        "<!-- learner mx_type=" + str(html["learner_has_mx"]) + " -->\n"
        + "<!-- teacher_has_mx_word=" + str(html["teacher_has_mx_word"]) + " -->\n",
        encoding="utf-8",
    )
    doc = {"ok": True, "stats": result["stats"], "html": html}
    text = json.dumps(doc, indent=2)
    log_path.write_text(text + "\n", encoding="utf-8")
    print(text)
