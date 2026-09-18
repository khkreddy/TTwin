#!/usr/bin/env python3
"""Tag unmapped TTwin questions onto existing maps.

K12 grades 6–8 science → science.json grains (S1–S6).
K12 maths → MATHEMATICS_MAP nodes (prefer g6–8).
JEE / Phy-500 / MathNet / … → existing chem/phy/bio/maths nodes, practice_tier=advanced.
Does not invent nodes. Does not rewrite maps or exam.v1.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from question_pack import (  # noqa: E402
    OUT,
    SUBJECT_ORDER,
    UNMAPPED,
    _tokens,
    dump_json,
    nav_from_item,
    prefix_node,
)

QDIR = OUT / "questions"
MAPS = OUT / "maps"
PENDING = OUT / "question_bank_pending.json"
PENDING_JSONL = OUT / "question_bank_pending.jsonl"
CJK = re.compile(r"[\u4e00-\u9fff]")
MIN_EN = 2

SCIENCE_GRAIN_KW = [
    ("S3/H-BODY", "S3", ["digest", "blood", "nutrition", "health", "food", "heart", "kidney", "lung", "diet", "glucose", "enzyme"],
     ["消化", "血液", "营养", "健康", "食物", "心脏", "肾", "肺", "口腔", "馒头", "血浆", "输血", "呼吸", "胸腔", "近视", "反射"]),
    ("S3/H-ECO", "S3", ["ecosystem", "habitat", "microbe", "bacteria", "virus", "food chain", "environment", "biosphere"],
     ["生态", "环境", "微生物", "细菌", "病毒", "食物链", "草原", "生物圈", "植被", "酸雨"]),
    ("S3/H-LIFE", "S3", ["cell", "plant", "animal", "seed", "photosynthesis", "chlorophyll", "genetic", "tissue", "organism", "living"],
     ["细胞", "植物", "动物", "种子", "光合", "叶绿素", "遗传", "组织", "器官", "生物", "花粉", "导管", "蒸腾", "发芽", "分裂"]),
    ("S2/H-CHANGE", "S2", ["chemical change", "physical change", "combustion", "reaction", "neutralis", "rust"],
     ["化学变化", "物理变化", "燃烧", "生锈", "中和", "化学", "反应"]),
    ("S2/H-MIXTURE", "S2", ["mixture", "solution", "separat", "filter", "evaporat", "distill", "pure substance"],
     ["混合物", "溶液", "分离", "过滤", "蒸发", "蒸馏", "纯净"]),
    ("S2/H-STATES", "S2", ["solid", "liquid", "gas", "particle", "melt", "freeze", "evaporat", "condens"],
     ["固体", "液体", "气体", "粒子", "分子", "熔化", "凝固", "蒸发"]),
    ("S2/H-MATERIAL", "S2", ["metal", "acid", "base", "salt", "material", "property", "indicator"],
     ["金属", "酸", "碱", "盐", "材料", "性质", "指示剂"]),
    ("S4/H-MAGNET", "S4", ["magnet", "magnetic", "compass", "pole"],
     ["磁", "磁铁", "磁极", "指南针"]),
    ("S4/H-FORCE", "S4", ["force", "pressure", "friction", "newton", "push", "pull"],
     ["力", "压力", "摩擦", "牛顿", "推力", "拉力"]),
    ("S4/H-MOTION", "S4", ["speed", "velocity", "motion", "acceleration", "distance", "time"],
     ["速度", "运动", "加速", "路程"]),
    ("S5/H-CIRCUIT", "S5", ["circuit", "current", "voltage", "battery", "cell", "resistor", "ohm"],
     ["电路", "电流", "电压", "电池", "电阻"]),
    ("S5/H-HEAT", "S5", ["heat", "temperature", "conduction", "convection", "radiation", "thermal"],
     ["热", "温度", "传导", "对流", "辐射"]),
    ("S5/H-LIGHT", "S5", ["light", "mirror", "lens", "reflect", "refract", "ray", "image"],
     ["光", "镜", "透镜", "反射", "折射"]),
    ("S6/H-SKY", "S6", ["moon", "sun", "star", "planet", "eclipse", "orbit", "calendar"],
     ["月", "太阳", "星", "地球自转", "公转", "日食", "月食"]),
    ("S6/H-EARTH", "S6", ["resource", "soil", "air", "water cycle", "habitab", "oxygen", "atmosphere"],
     ["资源", "土壤", "空气", "水循环", "大气"]),
    ("S1/H-INQUIRY", "S1", ["experiment", "observe", "hypothesis", "variable", "control", "scientific"],
     ["实验", "观察", "假设", "对照", "变量", "科学"]),
]

MATH_NODE_KW = [
    ("M1", ["number", "fraction", "decimal", "percent", "ratio", "integer", "prime", "divis"],
     ["分数", "小数", "百分", "比例", "整数", "质数", "因数", "有理", "实数", "正整数"]),
    ("M2", ["equation", "algebra", "polynomial", "factor", "identity", "express", "inequal", "set"],
     ["方程", "代数", "因式", "多项式", "恒等", "不等式", "集合", "解集"]),
    ("M3", ["function", "sequence", "mapping", "series", "arithmetic progression"],
     ["函数", "数列", "映射", "等差", "等比", "通项"]),
    ("M4", ["angle", "triangle", "circle", "parallel", "congruent", "similar", "proof"],
     ["角", "三角", "圆", "平行", "全等", "相似", "几何", "证明"]),
    ("M5", ["area", "volume", "perimeter", "trigon", "sine", "cosine"],
     ["面积", "体积", "周长", "正弦", "余弦", "正切"]),
    ("M6", ["coordinate", "vector", "graph", "slope"],
     ["坐标", "向量", "斜率", "立体", "空间"]),
    ("M7", ["limit", "derivative", "integral", "calculus"],
     ["极限", "导数", "积分", "微分"]),
    ("M8", ["probab", "statist", "mean", "median", "data"],
     ["概率", "统计", "平均", "中位数", "方差"]),
]

ADVANCED_BANKS = {
    "jeebench", "physics500", "phybench", "scibench", "superchem",
    "aime", "hicogmath", "mathnet",
}
SHEAF = {
    "S1": "B5", "S2": "C2", "S3": "L1", "S4": "P1", "S5": "P2", "S6": "B3",
}


def load_map_units(subject: str) -> list[dict]:
    path = MAPS / f"{subject}.json"
    if not path.is_file():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for u in doc.get("units") or []:
        node = u.get("node")
        if not node or str(node).upper() == "UNRESOLVED":
            continue
        law = u.get("mechanism")
        if isinstance(law, dict):
            law = law.get("law") or ""
        blob = " ".join(
            [
                str(u.get("chapter_title") or ""),
                str(u.get("decision_hinge") or u.get("statement") or ""),
                str(law or ""),
            ]
        )
        tok = _tokens(blob)
        if len(tok) < 3:
            continue
        out.append({"unit": u, "tok": tok, "grade": _grade_of(u.get("unit_id") or "")})
    return out


def _grade_of(unit_id: str) -> int | None:
    m = re.search(r"grade_(\d+)", unit_id)
    return int(m.group(1)) if m else None


def best_unit(qtok: set[str], index: list[dict], *, prefer_grades=None) -> tuple[dict | None, int]:
    best, best_n = None, 0
    for row in index:
        if prefer_grades is not None and row["grade"] not in prefer_grades:
            continue
        n = len(qtok & row["tok"])
        if n > best_n:
            best, best_n = row["unit"], n
    if best is None and prefer_grades is not None:
        return best_unit(qtok, index, prefer_grades=None)
    return best, best_n


def kw_science(stem: str) -> tuple[str, str, int] | None:
    text = stem or ""
    low = text.lower()
    best, best_n = None, 0
    for grain, parent, en, zh in SCIENCE_GRAIN_KW:
        n = 0
        for w in zh:
            if w and w in text:
                n += 3
        for w in en:
            if w and w in low:
                n += 2
        if n > best_n:
            best, best_n = (grain, parent), n
    if best and best_n >= 2:
        return best[0], best[1], best_n
    return None


def kw_math(stem: str) -> tuple[str, int] | None:
    text = stem or ""
    low = text.lower()
    best, best_n = None, 0
    for node, en, zh in MATH_NODE_KW:
        n = 0
        for w in zh:
            if w and w in text:
                n += 3
        for w in en:
            if w and w in low:
                n += 2
        if n > best_n:
            best, best_n = node, n
    if best and best_n >= 2:
        return best, best_n
    return None


def rjb_grade(uid: str) -> int | None:
    m = re.search(r"_(\d+)[ab]_rjb", uid or "")
    if m:
        return int(m.group(1))
    m = re.search(r"grade[_-]?(\d+)", uid or "", re.I)
    return int(m.group(1)) if m else None


def apply_science(it: dict, grain: str, parent: str, unit: dict | None) -> None:
    it["node"] = grain
    it["chapter_id"] = (unit or {}).get("chapter") or (unit or {}).get("unit_id") or grain
    it["chapter_label"] = (unit or {}).get("chapter_title") or parent
    it["subtopic_id"] = (unit or {}).get("unit_id") or grain
    it["subtopic_label"] = ((unit or {}).get("decision_hinge") or grain)[:80]
    it["ncert_family"] = SHEAF.get(parent)
    it["science_grain"] = grain
    it["science_node"] = parent
    it["practice_tier"] = "core"


def apply_map(it: dict, subject: str, unit: dict, *, advanced: bool) -> None:
    node = unit.get("node") or ""
    it["node"] = prefix_node(subject, node) if ":" not in str(node) else node
    uid = unit.get("unit_id") or node
    it["chapter_id"] = uid
    it["chapter_label"] = unit.get("chapter_title") or unit.get("chapter") or subject
    it["subtopic_id"] = uid
    it["subtopic_label"] = (unit.get("decision_hinge") or unit.get("statement") or "")[:80]
    if str(uid).startswith(("IGCSE:", "AS_A:")):
        it["cam_family"] = uid
    elif str(uid).startswith(("science/", "math/")):
        it["ncert_family"] = uid
    it["practice_tier"] = "advanced" if advanced else "core"


def tag_item(it: dict, indexes: dict[str, list]) -> str | None:
    """Return how tagged, or None if still unmapped."""
    uid = it.get("uid") or ""
    stem = str(it.get("stem") or it.get("stem_lead") or "")
    subj = it.get("subject")
    bank = it.get("bank") or ""
    advanced = bank in ADVANCED_BANKS
    qtok = _tokens(stem)
    cjk = bool(CJK.search(stem))
    g = rjb_grade(uid)

    # K12 / junior science → science 6–8 map
    if bank == "k12_graph" and subj in {"chemistry", "biology", "physics"}:
        junior = g is None or g <= 8
        if junior:
            hit = kw_science(stem)
            sci_idx = indexes["science"]
            unit, n = (None, 0)
            if qtok:
                prefer = {6, 7, 8}
                unit, n = best_unit(qtok, sci_idx, prefer_grades=prefer)
            if hit and (not unit or hit[2] >= n):
                grain, parent, _sc = hit
                # pick a representative unit of that grain if possible
                u2 = next((r["unit"] for r in sci_idx if r["unit"].get("node") == grain), None)
                apply_science(it, grain, parent, u2)
                return "science_kw"
            if unit and n >= MIN_EN:
                grain = unit.get("node")
                parent = unit.get("node_parent") or str(grain).split("/")[0]
                apply_science(it, grain, parent, unit)
                return "science_overlap"
            if hit:
                apply_science(it, hit[0], hit[1], None)
                return "science_kw"
        # grade 9+ k12 science → subject maps
        idx = indexes.get(subj) or []
        unit, n = best_unit(qtok, idx) if qtok else (None, 0)
        if unit and n >= MIN_EN:
            apply_map(it, subj, unit, advanced=False)
            return "subject_g9"
        hit = kw_science(stem)
        if hit:
            apply_science(it, hit[0], hit[1], None)
            return "science_kw_g9"

    # K12 maths (incl. primary/junior)
    if bank == "k12_graph" and subj == "maths":
        prefer = {6, 7, 8} if (g is None or 6 <= g <= 8) else ({g} if g else None)
        unit, n = best_unit(qtok, indexes["maths"], prefer_grades=prefer) if qtok else (None, 0)
        if unit and n >= MIN_EN:
            apply_map(it, "maths", unit, advanced=False)
            return "maths_overlap"
        mh = kw_math(stem)
        if mh:
            node, _sc = mh
            dummy = {"node": node, "unit_id": f"math:{node}", "chapter_title": node, "decision_hinge": node}
            apply_map(it, "maths", dummy, advanced=False)
            return "maths_kw"

    # exam remainder → subject maps
    if bank == "exam_v1_held" and subj in indexes:
        unit, n = best_unit(qtok, indexes[subj]) if qtok else (None, 0)
        if unit and n >= MIN_EN:
            apply_map(it, subj, unit, advanced=False)
            return "exam_overlap"

    # advanced practice → existing map nodes
    if advanced and subj in indexes:
        unit, n = best_unit(qtok, indexes[subj]) if qtok else (None, 0)
        if unit and n >= 1:
            apply_map(it, subj, unit, advanced=True)
            return "advanced_overlap"
        if subj == "maths":
            mh = kw_math(stem)
            if mh:
                dummy = {"node": mh[0], "unit_id": f"math:{mh[0]}", "chapter_title": mh[0], "decision_hinge": mh[0]}
                apply_map(it, "maths", dummy, advanced=True)
                return "advanced_kw"
        if subj in {"chemistry", "biology", "physics"}:
            hit = kw_science(stem)
            if hit:
                # map science grain to sheaf home on the subject map
                parent = hit[1]
                sheaf = SHEAF.get(parent)
                dummy = {"node": sheaf or parent, "unit_id": hit[0], "chapter_title": hit[0], "decision_hinge": hit[0]}
                apply_map(it, subj, dummy, advanced=True)
                it["science_grain"] = hit[0]
                return "advanced_sci_kw"

    # last chance: any map for this subject
    if subj in indexes and qtok:
        unit, n = best_unit(qtok, indexes[subj])
        if unit and n >= 1:
            apply_map(it, subj, unit, advanced=advanced)
            return "fallback_overlap"
    # K12 leftover: still a real map node, coarsest grain for the subject
    if bank == "k12_graph":
        if subj == "maths":
            node = "M2" if ("$" in stem or "\\" in stem) else "M1"
            dummy = {"node": node, "unit_id": f"math:{node}", "chapter_title": node, "decision_hinge": node}
            apply_map(it, "maths", dummy, advanced=False)
            return "maths_default"
        grain, parent = {
            "biology": ("S3/H-LIFE", "S3"),
            "chemistry": ("S2/H-MATERIAL", "S2"),
            "physics": ("S4/H-FORCE", "S4"),
        }.get(subj, (None, None))
        if grain:
            apply_science(it, grain, parent, None)
            return "science_default"
    return None


def main() -> int:
    print("loading maps…")
    indexes = {
        "science": load_map_units("science"),
        "maths": load_map_units("maths"),
        "chemistry": load_map_units("chemistry"),
        "physics": load_map_units("physics"),
        "biology": load_map_units("biology"),
    }
    print({k: len(v) for k, v in indexes.items()})
    how = Counter()
    n_before = n_after = 0
    nav_by = defaultdict(list)
    for path in sorted(QDIR.glob("*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for it in rows:
            if it.get("node") == UNMAPPED:
                n_before += 1
                reason = tag_item(it, indexes)
                if reason:
                    how[reason] += 1
                    changed = True
                else:
                    n_after += 1
            nav_by[it.get("subject")].append(nav_from_item(it))
        if changed:
            dump_json(path, rows)
            print("  wrote", path.name)
        else:
            print("  skip", path.name)
    for subject in SUBJECT_ORDER:
        rows = nav_by.get(subject) or []
        rows.sort(key=lambda r: (r.get("pack") or "", r.get("uid") or ""))
        dump_json(OUT / "nav" / f"{subject}.json", rows)

    still = []
    if PENDING_JSONL.is_file():
        for line in PENDING_JSONL.open(encoding="utf-8"):
            row = json.loads(line)
            if row.get("task") == "node_map":
                continue
            still.append(row)
        # re-add remaining unmapped as node_map
        for path in QDIR.glob("*.json"):
            for it in json.loads(path.read_text(encoding="utf-8")):
                if it.get("node") == UNMAPPED:
                    still.append({"uid": it.get("uid"), "task": "node_map", "origin": it.get("bank") or "unknown"})
        with PENDING_JSONL.open("w", encoding="utf-8") as fh:
            for row in still:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    pending_doc = {}
    if PENDING.is_file():
        pending_doc = json.loads(PENDING.read_text(encoding="utf-8"))
    pending_doc["n_unmapped_before"] = n_before
    pending_doc["n_unmapped_after"] = n_after
    pending_doc["tagged_how"] = dict(how)
    pending_doc["pending_by_task"] = dict(Counter(r.get("task") for r in still))
    dump_json(PENDING, pending_doc)
    print(json.dumps({"unmapped_before": n_before, "unmapped_after": n_after, "how": dict(how)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
