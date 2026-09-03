/* Deterministic retrieve. Zero provider calls. Port of nav_mcq_rag ancestor closure. */
(function (g) {
  const PACK = {
    A: "igcse_9_10",
    B: "senior_11_12_as_a",
    C: "olympiad_iit",
    igcse_9_10: "igcse_9_10",
    senior_11_12_as_a: "senior_11_12_as_a",
    olympiad_iit: "olympiad_iit",
    igcse: "igcse_9_10",
    as: "senior_11_12_as_a",
    "as-a": "senior_11_12_as_a",
    "a-level": "senior_11_12_as_a",
    senior: "senior_11_12_as_a",
    olympiad: "olympiad_iit",
    iit: "olympiad_iit",
  };
  const PACK_BAND = {
    igcse_9_10: "SECONDARY",
    senior_11_12_as_a: "SENIOR_SECONDARY",
    olympiad_iit: "olympiad-iit",
  };
  const CAP = 32;
  const JUNIOR_H007 = "science/grade_10/ch_01/H007";
  const C6_A2 = "AS_A:9701.23";
  const C6_AS = "AS_A:9701.5";

  function normNode(n) {
    const s = String(n || "").trim();
    if (s.startsWith("chem:")) return s.slice(5);
    const i = s.indexOf(":");
    if (i > 0 && ["phy", "bio", "math"].includes(s.slice(0, i))) return s.slice(i + 1);
    return s;
  }
  function nodeChain(n) {
    const bare = normNode(n);
    if (!bare) return [];
    const parts = bare.split("/").filter(Boolean);
    const out = [parts[0]];
    for (let i = 1; i < parts.length; i++) out.push(out[out.length - 1] + "/" + parts[i]);
    return out;
  }
  function nodesComparable(a, b) {
    const ca = nodeChain(a), cb = nodeChain(b);
    if (!ca.length || !cb.length) return false;
    if (ca.join() === cb.join()) return true;
    if (ca.length < cb.length && cb.slice(0, ca.length).join() === ca.join()) return true;
    if (cb.length < ca.length && ca.slice(0, cb.length).join() === cb.join()) return true;
    return false;
  }
  function normalizePack(p) {
    if (p == null || p === "") return null;
    const k = String(p).trim();
    if (PACK[k]) return PACK[k];
    return PACK[k.toLowerCase()] || null;
  }
  function bandForPack(p) {
    return PACK_BAND[normalizePack(p)] || null;
  }
  function parseCam(fid) {
    const s = String(fid || "").trim();
    let m = s.match(/^cam:(\d{4}):(.+)$/);
    if (m) return ["cam", m[1]].concat(String(m[2]).split(/[.:]/).filter(Boolean));
    m = s.match(/^(IGCSE|AS_A):(\d{4})\.(.+)$/);
    if (m) return ["cam", m[2]].concat(String(m[3]).split(".").filter(Boolean));
    return null;
  }
  function parseNcert(fid) {
    let s = String(fid || "").trim();
    if (s.startsWith("ncert:")) s = s.slice(6);
    if (s.startsWith("science/")) return s.split("/");
    return null;
  }
  function coordsComparable(a, b) {
    if (!a || !b) return false;
    if (a.join() === b.join()) return true;
    const short = a.length < b.length ? a : b;
    const long = a.length < b.length ? b : a;
    return long.slice(0, short.length).join() === short.join();
  }
  function familiesComparable(a, b) {
    const ca = parseCam(a), cb = parseCam(b);
    if (ca && cb) return coordsComparable(ca, cb);
    const na = parseNcert(a), nb = parseNcert(b);
    if (na && nb) return coordsComparable(na, nb);
    return false;
  }
  function camChapterPrefix(uid) {
    const m = String(uid || "").match(/^(IGCSE:0620|AS_A:9701)\.(\d+)/);
    return m ? m[1] + "." + m[2] : null;
  }
  function namedFamily(table, fid) {
    const recs = (table && table.named_families) || {};
    if (recs[fid]) return recs[fid];
    const low = String(fid || "").toLowerCase();
    for (const k of Object.keys(recs)) if (k.toLowerCase() === low) return recs[k];
    return null;
  }
  function itemCamFamilies(row) {
    const out = [];
    if (row.cam_family) out.push(row.cam_family);
    if (row.chapter_id) out.push(row.chapter_id);
    if (row.subtopic_id) out.push(row.subtopic_id);
    return out;
  }
  function itemNcertFamilies(row) {
    const out = [];
    if (row.ncert_family) out.push(String(row.ncert_family).replace(/^ncert:/, ""));
    return out;
  }
  function itemMatchesFamily(row, fam, table) {
    const named = namedFamily(table, fam);
    if (named) {
      const nodes = named.nodes || [];
      if (!nodes.length) return false;
      return nodes.some((n) => nodesComparable(row.node, n));
    }
    if (parseCam(fam)) {
      const itemFams = itemCamFamilies(row);
      if (!itemFams.length) return true;
      return itemFams.some((ex) => familiesComparable(ex, fam));
    }
    if (parseNcert(fam) || String(fam).startsWith("ncert:") || String(fam).startsWith("science/")) {
      const itemFams = itemNcertFamilies(row);
      if (!itemFams.length) return false;
      const want = String(fam).replace(/^ncert:/, "");
      return itemFams.some((ex) => familiesComparable(ex, want) || familiesComparable("ncert:" + ex, fam));
    }
    return false;
  }
  function selectorBand(sel, table) {
    const pack = normalizePack(sel.pack);
    if (pack) return bandForPack(pack);
    const uid = sel.unit_id;
    if (uid && table) {
      for (const rec of table.ncert || []) if (rec.unit_id === uid) return rec.grade_band;
      for (const rec of table.cambridge || []) if (rec.unit_id === uid) return rec.grade_band;
    }
    return null;
  }
  function mapsOf(sel) {
    const raw = sel.maps;
    if (!raw || !raw.length) return new Set(["ncert", "cambridge"]);
    return new Set(raw.map((m) => String(m).toLowerCase()));
  }
  function asksLattice(sel) {
    const blob = JSON.stringify(sel).toLowerCase();
    return /lattice|born.?haber|entropy|9701\.23|9701:23/.test(blob);
  }
  function itemMatches(row, sel, table) {
    if ((row.status || "tagged") !== "tagged") return false;
    const subj = String(sel.subject || "chemistry").toLowerCase();
    if (subj && subj !== "any" && (row.subject || "chemistry") !== subj) return false;
    const wantPack = normalizePack(sel.pack);
    const rowPack = row.pack;
    const rowBand = row.grade_band || bandForPack(rowPack);
    const selB = selectorBand(sel, table);
    if (wantPack) {
      if (rowPack !== wantPack) return false;
    } else if (sel.unit_id && selB && rowBand !== selB) return false;
    let nodes = (sel.nodes || []).map(String).filter(Boolean);
    if (sel.unit_id && !nodes.length) {
      for (const rec of (table && table.ncert) || []) {
        if (rec.unit_id === sel.unit_id) { nodes = ["chem:" + rec.node]; break; }
      }
    }
    for (const node of nodes) {
      if (!nodesComparable(row.node, node)) return false;
    }
    let families = (sel.families || []).map(String).filter(Boolean);
    if (sel.unit_id && !families.length) {
      for (const rec of (table && table.ncert) || []) {
        if (rec.unit_id === sel.unit_id && rec.chapter_family) {
          families = [rec.chapter_family];
          break;
        }
      }
    }
    for (const fam of families) {
      if (!itemMatchesFamily(row, fam, table)) return false;
    }
    return true;
  }
  function ncertHinges(table, node, band) {
    const want = normNode(node);
    return (table.ncert || [])
      .filter((r) => r.grade_band === band && nodesComparable(r.node, want))
      .map((r) => r.unit_id);
  }
  function cambridgeHinges(table, node, band, includeA2) {
    const want = normNode(node);
    const out = [];
    for (const rec of table.cambridge || []) {
      if (rec.grade_band !== band) continue;
      if (!nodesComparable(rec.node, want)) continue;
      const uid = rec.unit_id;
      const chp = rec.chapter_prefix || camChapterPrefix(uid);
      if (want === "C6" && band === "SENIOR_SECONDARY" && chp === C6_A2 && !includeA2) continue;
      if (want === "C6" && band === "SENIOR_SECONDARY" && !includeA2 && chp && chp !== C6_AS) continue;
      out.push(uid);
    }
    return out;
  }
  function collectHinges(sel, table) {
    const maps = mapsOf(sel);
    const band = selectorBand(sel, table);
    const related = !!sel.related_lower_grain;
    const includeA2 = asksLattice(sel);
    const found = new Set();
    if (sel.unit_id) found.add(String(sel.unit_id));
    let nodes = (sel.nodes || []).map(String).filter(Boolean);
    if (sel.unit_id && !nodes.length) {
      for (const rec of table.ncert || []) {
        if (rec.unit_id === sel.unit_id) { nodes = ["chem:" + rec.node]; break; }
      }
    }
    const bands = band ? [band] : [];
    if (related && band === "SENIOR_SECONDARY") bands.push("SECONDARY");
    for (const node of nodes) {
      for (const b of bands) {
        if (!b || b === "olympiad-iit") continue;
        if (maps.has("ncert")) ncertHinges(table, node, b).forEach((u) => found.add(u));
        if (maps.has("cambridge")) cambridgeHinges(table, node, b, includeA2).forEach((u) => found.add(u));
      }
    }
    for (const fam of sel.families || []) {
      const named = namedFamily(table, fam);
      if (named && named.unit_ids) {
        const allowed = new Set((table.ncert || []).filter((r) => !band || r.grade_band === band || (related && r.grade_band === "SECONDARY")).map((r) => r.unit_id));
        named.unit_ids.forEach((u) => { if (!band || allowed.has(u)) found.add(u); });
      }
      const parsed = parseCam(fam);
      if (parsed && maps.has("cambridge") && parsed.length >= 3) {
        const code = parsed[1], ch = parsed[2];
        const prefix = (code === "0620" ? "IGCSE:0620" : "AS_A:9701") + "." + ch;
        for (const rec of table.cambridge || []) {
          const uid = rec.unit_id;
          if (!(uid === prefix || uid.startsWith(prefix + "."))) continue;
          if (band && rec.grade_band !== band && !(related && rec.grade_band === "SECONDARY")) continue;
          if ((rec.chapter_prefix || camChapterPrefix(uid)) === C6_A2 && !includeA2) continue;
          found.add(uid);
        }
      }
    }
    if (!related && band === "SENIOR_SECONDARY") found.delete(JUNIOR_H007);
    return Array.from(found).sort();
  }
  function assemble(sel, navRows, table) {
    const questions = (navRows || []).filter((r) => itemMatches(r, sel, table));
    const uids = questions.map((r) => r.uid || r.item_uid).filter(Boolean).sort();
    const unitIds = collectHinges(sel, table);
    const truncated = unitIds.length > CAP;
    const kept = unitIds.slice(0, CAP);
    return {
      question_uids: uids,
      hinge_unit_ids: kept,
      hinge_unit_ids_all: unitIds,
      receipt: {
        provider_calls: 0,
        HINGE_PACK_CAP: CAP,
        n_questions: uids.length,
        n_hinge_unit_ids_before_cap: unitIds.length,
        truncated,
        truncation_silent: false,
        pack: normalizePack(sel.pack),
        grade_band: selectorBand(sel, table),
        related_lower_grain: !!sel.related_lower_grain,
        maps: Array.from(mapsOf(sel)).sort(),
      },
    };
  }
  function hingePack(unitId, hinges, enrichment) {
    const stmt = (hinges || []).find((h) => h.unit_id === unitId);
    const items = (enrichment || []).filter((e) => (e.serves || []).includes(unitId)).slice(0, 8);
    return {
      schema: "awm.hinge_pack.v1",
      unit_id: unitId,
      statement: stmt || null,
      enrichment: { n_in_packet: items.length, cap: 8, items },
    };
  }
  function parsePromptDeterministic(text, table) {
    const raw = String(text || "");
    const low = raw.toLowerCase();
    const sel = { subject: (table && table.subject) || "chemistry", maps: ["ncert", "cambridge"], nodes: [], families: [] };
    const aliases = (table && table.aliases) || {};
    const keys = Object.keys(aliases).sort((a, b) => b.length - a.length);
    for (const k of keys) {
      if (!k) continue;
      if (low.includes(k.toLowerCase())) {
        const a = aliases[k] || {};
        if (a.pack) sel.pack = normalizePack(a.pack) || a.pack;
        if (a.grade_band) sel.grade_band = a.grade_band;
        if (a.nodes) a.nodes.forEach((n) => { if (!sel.nodes.includes(n)) sel.nodes.push(n); });
        if (a.families) a.families.forEach((n) => { if (!sel.families.includes(n)) sel.families.push(n); });
        if (a.grain === "lattice_entropy") sel.related_lattice = true;
      }
    }
    if (/grade\s*9|igcse|gcse/.test(low) && !sel.pack) sel.pack = "igcse_9_10";
    if (/related lower|junior grain/.test(low)) sel.related_lower_grain = true;
    const um = raw.match(/science\/grade_\d+\/[^\s,]+\/H\d+/);
    if (um) sel.unit_id = um[0];
    if (!sel.nodes.length) delete sel.nodes;
    if (!sel.families.length) delete sel.families;
    return sel;
  }
  function mulberry32(a) {
    return function () {
      let t = (a += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function seededShuffle(arr, seed) {
    const out = arr.slice();
    if (seed == null || seed === "") return out.sort();
    let n = 0;
    const s = String(seed);
    for (let i = 0; i < s.length; i++) n = (n * 33 + s.charCodeAt(i)) >>> 0;
    const rnd = mulberry32(n || 1);
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(rnd() * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }
  g.TTwinRag = {
    assemble,
    hingePack,
    parsePromptDeterministic,
    normalizePack,
    bandForPack,
    nodesComparable,
    seededShuffle,
    CAP,
    PACK_BAND,
  };
})(window);
