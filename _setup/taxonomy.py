# -*- coding: utf-8 -*-
"""失败归因 taxonomy（零 GPU，只读评测产物）——把 QA 错题按「gold 的值/单位到底在不在模型眼前」分级。

动机：`D2D-Twin项目完整报告.md` §1 用「上游丢失 40-45% 跨 3B→14B 不变」作为 D2D-Twin 的立项依据，
但此前没有任何脚本产出过这组数（2026-10-07 扫描确认）。本脚本把它变成可复现产物。

== 三档值匹配（同一 gold，不同宽容度；报区间不报单点）==
  L1 strict : score2.items 逐字口径（判分器同源，不改判分器）。数值后 9 字符内接单位，
              且单位后紧跟字母视为伪匹配。
  L3 line   : 同一行内数值与单位 40 字符窗口共现（`|` 与制表符视作空格）。
  L4 block  : 整段合并（换行→空格）后同样 40 字符窗口共现——最宽，只用于判定「值与单位在文本里
              到底能不能配上」。
  为什么需要 L3/L4：语料是表格扁平化产物，实测三种拆散形态——
              `| 45 | °C/W |`（单元格分隔）、`147\nHz`（每格一行）、`266 mAP-P`（单位与下列标签粘连）。
              它们在 L1/L3 下都判「值不存在」，会把**结构脱钩**错算成**解析丢失**。
  字形：两侧都先 NFKC（语料混用 Ω U+03A9 / OHM-SIGN U+2126、℃ U+2103）。数值尾零规范化（4.70≡4.7）。

== 归因阶梯（主口径 L4；只对错题分类）==
  gen_side            值+单位在 ctx 里仍答错          → 生成侧
  retrieval_miss      值+单位在本文档、没进 ctx        → 检索漏捞
  binding_lost        数值在本文档、但任何档都配不到单位 → **表格扁平化把值与单位拆散**（结构丢失）
  collision_elsewhere 本档无此数值、别档有             → 跨文档值碰撞（该题不可检索，单列）
  value_absent        全语料无此数值                   → 真·解析丢失（值只活在图里）
  「上游丢失」= 除 gen_side 外全部；头条同时给 L1/L3 的 sensitivity 区间。

== 其它协议 ==
  · 跨 seed 两种定义都出：all3=该题 3 个 seed 全错；maj=≥2/3 错。逐数标源。
  · 分辨率说出口：per-question Wilson 95%CI + 跨规模同题配对 McNemar 精确检验；
    「不变」只能写成「差值低于 X pp 时检验不出」。
  · ctx 重构保真自检：逐组核对「重建 sources == 结果文件存储 sources」，<90% 的组剔除；k 自动探测。
  · 分层人工分诊 CSV（含空「人工裁决」列）：优先 L 档之间判类不一致的题——机器预标不作数。

用法（项目根）: python _setup/taxonomy.py [--groups DCU-3B,DCU-14B] [--spot 15]
产物: eval/qa100/taxonomy_summary.json / taxonomy_per_question.csv / taxonomy_spotcheck15.csv
"""
import sys, os, json, re, csv, math, argparse, collections, itertools, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval", "qa100"))
sys.stdout.reconfigure(encoding="utf-8")

from score2 import items as s2_items, NUM_RX as s2_NUM, UNIT_RX as s2_UNIT, norm_unit
from run import build_ctx                 # 上下文构造与 run.py 完全同源
from rag.hierarchical import HierarchicalRetriever

DS_V3 = "eval/qa100/datasheet_qa100_v3.json"
DS_V6 = "eval/qa100/datasheet_qa100_v6.json"
OUT_DIR = os.path.join(ROOT, "eval", "qa100")

RUNS = [
    ("DCU-3B",       ["eval/qa100/results_dcu3b_kt_s%d.json" % s for s in (1, 2, 3)], DS_V3, "bf16+eager"),
    ("DCU-7B",       ["eval/qa100/results_dcu7b_kt_s%d.json" % s for s in (1, 2, 3)], DS_V3, "bf16+eager"),
    ("DCU-14B",      ["eval/qa100/results_dcu14b_kt_s%d.json" % s for s in (1, 2, 3)], DS_V3, "bf16+eager"),
    ("Local-3B-q4",  ["eval/qa100/results_kt_rag3b_s%d.json" % s for s in (1, 2, 3)], DS_V3, "Ollama q4_K_M"),
    ("Local-7B-loose", ["eval/qa100/results_kt_rag7b_s%d.json" % s for s in (1, 2, 3)], DS_V3, "Ollama q4_K_M+loose"),
    ("API-rag",      ["eval/qa100/results_v31_api_rag.json"], DS_V3, "商用API 单seed"),
    ("App-7B-loose", ["eval/qa100/results_app36_7bloose.json"], DS_V6, "app 题型批次三 36 题"),
]
LEVELS = ("strict", "line", "block")
PRIMARY = "block"
NOT_GEN = ("retrieval_miss", "binding_lost", "collision_elsewhere", "value_absent")
CAT_ORDER = ("gen_side", "retrieval_miss", "binding_lost", "collision_elsewhere", "value_absent", "unjudgeable")


def nfk(s):
    return unicodedata.normalize("NFKC", s)


def canon_num(s):
    try:
        f = float(s)
    except ValueError:
        return s
    if f == int(f):
        return str(int(f))
    return repr(f).rstrip("0").rstrip(".")


UNIT_WINDOW = 40
SEP_RX = re.compile(r"[|\t]+")


def _units_near(nums_iter, text):
    """在 text 里对每个数值取其后 UNIT_WINDOW 字符内的所有独立单位 token。"""
    ps, ns = set(), set()
    for m in s2_NUM.finditer(text):
        num = canon_num(m.group(0))
        ns.add(num)
        tail = text[m.end():m.end() + UNIT_WINDOW]
        for um in LINE_UNIT_RX.finditer(tail):
            ps.add((num, norm_unit(um.group(0))))
    return ps, ns


LINE_UNIT_RX = re.compile(r"(?<![A-Za-z])(?:" + s2_UNIT.pattern + r")(?![A-Za-z])")


def pairs_at(text, level):
    """按宽容度取 (数值,单位) 集合与数值集合。"""
    t = nfk(text)
    if level == "strict":
        ps, ns = set(), set()
        for num, unit in s2_items(t):
            c = canon_num(num)
            ps.add((c, unit)); ns.add(c)
        return ps, ns
    if level == "line":
        ps, ns = set(), set()
        for raw in t.split("\n"):
            line = re.sub(r"\s+", " ", SEP_RX.sub(" ", raw)).strip()
            if not line:
                continue
            p2, n2 = _units_near(None, line)
            ps |= p2; ns |= n2
        return ps, ns
    # block: 换行也压成空格（最宽——只用来问「值与单位到底能不能配上」）
    joined = re.sub(r"\s+", " ", SEP_RX.sub(" ", t))
    return _units_near(None, joined)


PART_PREFIX = re.compile(r"^[A-Za-z][A-Za-z0-9\-_. ]*?\s*[:：]\s*")


def gold_pairs(gold, qtype):
    """cross gold 形如 'PART:值|PART:值'，型号名里的数字会污染数值（LM2596→2596），先剥前缀。"""
    segs = gold.split("|") if qtype == "cross" else [gold]
    out = []
    for s in segs:
        out += [(canon_num(n), u) for n, u in s2_items(nfk(PART_PREFIX.sub("", s)))]
    return out


def gold_nums(gpairs):
    return set(n for n, _ in gpairs)


def present_pair(gpairs, pset):
    if not gpairs:
        return None
    return all((n, u) in pset if u else True for n, u in gpairs)


def present_num(gpairs, nset):
    """只要求数值本身出现（单位能否配上另说）。"""
    if not gpairs:
        return None
    return gold_nums(gpairs) <= nset


def gold_repr(gpairs):
    return "|".join("%s%s" % (n, (" " + u) if u else "") for n, u in gpairs)


def categorize(gpairs, in_ctx, in_doc, num_in_doc, in_corpus, num_in_corpus):
    if not gpairs:
        return "unjudgeable"
    if in_ctx:
        return "gen_side"
    if in_doc:
        return "retrieval_miss"
    if num_in_doc:
        return "binding_lost"
    if num_in_corpus and not in_corpus:
        return "collision_elsewhere"
    if in_corpus:
        return "collision_elsewhere"
    return "value_absent"


class Index:
    """一次遍历语料，为每档匹配建立 corpus 与 文档 两级集合。"""

    def __init__(self, retr):
        self.retr = retr
        self.c_pair = {l: set() for l in LEVELS}
        self.c_num = {l: set() for l in LEVELS}
        self.d_pair = {l: collections.defaultdict(set) for l in LEVELS}
        self.d_num = {l: collections.defaultdict(set) for l in LEVELS}
        for c in retr.chunks:
            for lvl in LEVELS:
                ps, ns = pairs_at(c.text, lvl)
                self.c_pair[lvl] |= ps; self.c_num[lvl] |= ns
                self.d_pair[lvl][c.doc_id] |= ps; self.d_num[lvl][c.doc_id] |= ns

    def doc_sets(self, part, level):
        dids = self.retr._doc_ids_for_part(part) if part else []
        p, n = set(), set()
        for did in dids:
            p |= self.d_pair[level][did]; n |= self.d_num[level][did]
        return p, n, len(dids)


def build_ctx_map(retr, qs, k):
    return {q["qid"]: build_ctx(retr, q, k) for q in qs}


def detect_k(retr, qs, stored_sources):
    best, best_rate = None, -1.0
    for k in (3, 5):
        cm = build_ctx_map(retr, qs, k)
        hit = sum(1 for q in qs if [h["chunk_id"] for h in cm[q["qid"]][1]] == stored_sources.get(q["qid"]))
        rate = hit / len(qs)
        if rate > best_rate:
            best, best_rate = k, rate
    return best, best_rate


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d) * 100, min(1.0, (c + h) / d) * 100)


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", default=None)
    ap.add_argument("--spot", type=int, default=15)
    args = ap.parse_args()
    only = [g.strip() for g in args.groups.split(",")] if args.groups else None

    retr = HierarchicalRetriever()
    print("[索引] 逐切片建三档 (数值,单位) 集合 …", flush=True)
    idx = Index(retr)
    print("[索引] 切片 %d / 文档 %d / 数值项 L1=%d L3=%d L4=%d" % (
        len(retr.chunks), len(retr.docs), len(idx.c_pair["strict"]),
        len(idx.c_pair["line"]), len(idx.c_pair["block"])), flush=True)

    summary = {"protocol": {
        "matcher_levels": "L1=score2 逐字 / L3=同行 40 字符窗口 / L4=整段合并 40 字符窗口（头条用 L4）",
        "normalization": "两侧 NFKC（Ω U+03A9 / OHM-SIGN U+2126 / ℃ U+2103）+ 数值尾零规范化",
        "ladder": {"gen_side": "值+单位在 ctx 仍错", "retrieval_miss": "值+单位在本档、没进 ctx",
                   "binding_lost": "数值在本档但配不到单位＝表格扁平化结构丢失",
                   "collision_elsewhere": "本档无此数值、别档有", "value_absent": "全语料无此数值＝真解析丢失"},
        "upstream": list(NOT_GEN),
        "seed_defs": {"all3": "3 个 seed 全错", "maj": "≥2/3 seed 错"},
        "scope": "ctx(含 context_for_parts 的 per 字符截断) ⊂ doc(该型号全文档) ⊂ corpus(全语料)",
        "caveat_model_independence": "类别只由「固定 k=5 检索出的 ctx + 语料文本」决定，与被测模型无关。"
                                     "因此「上游丢失率跨规模不变」接近同义反复，不能作为规模鲁棒性的证据；"
                                     "规模效应必须看 scale_rescue（哪些题被救回、属于哪一类）。"},
        "groups": [], "invariance_tests": {}, "per_question_rows": 0}

    qs_by_ds, ctx_by_group, rows_all = {}, {}, []
    for name, files, ds, note in RUNS:
        if only and name not in only:
            continue
        if ds not in qs_by_ds:
            qs_by_ds[ds] = json.load(open(os.path.join(ROOT, ds), encoding="utf-8"))
        qs = qs_by_ds[ds]
        per_seed = []
        for fp in files:
            p = os.path.join(ROOT, fp)
            if os.path.exists(p):
                per_seed.append(json.load(open(p, encoding="utf-8")))
        if not per_seed:
            print("[跳过] 无结果文件", name); continue

        stored = {x["qid"]: list(x.get("sources") or []) for x in per_seed[0]}
        k, k_rate = detect_k(retr, qs, stored)
        ctx_map = build_ctx_map(retr, qs, k)
        match = sum(1 for qid, src in stored.items()
                    if [h["chunk_id"] for h in ctx_map[qid][1]] == src)
        fidelity = match / len(stored)
        seed_tot = sum(len(r) for r in per_seed)
        seed_agree = sum(1 for rows in per_seed for x in rows if list(x.get("sources") or []) == stored.get(x["qid"]))
        g = {"group": name, "files": [os.path.basename(f) for f in files], "dataset": os.path.basename(ds),
             "k_inferred": k, "k_detect_rate": round(k_rate, 4), "n_seeds": len(per_seed),
             "ctx_reconstruction_fidelity": round(fidelity, 4),
             "sources_identical_across_seeds": "%d/%d" % (seed_agree, seed_tot), "note": note}
        if fidelity < 0.90:
            g["status"] = "EXCLUDED: ctx 重构保真 <90%，当时检索协议与现 build_ctx 不同，无法断言「在不在模型眼前」"
            summary["groups"].append(g)
            print("[剔除] %-16s fidelity=%.1f%%" % (name, fidelity * 100), flush=True)
            continue
        g["status"] = "ok"

        ctx_sets = {lvl: {qid: pairs_at(ctx_map[qid][0], lvl) for qid in ctx_map} for lvl in LEVELS}
        per_q = {}
        for q in qs:
            if q["qid"] not in stored:
                continue
            gp = gold_pairs(q["gold"], q["type"])
            parts = ([s.split(":")[0].strip() for s in q["gold"].split("|")]
                     if q["type"] == "cross" else [q.get("part") or ""])
            cats, flags = {}, {}
            for lvl in LEVELS:
                dp, dn, nd = set(), set(), 0
                for p in parts:
                    p2, n2, nd2 = idx.doc_sets(p, lvl)
                    dp |= p2; dn |= n2; nd = max(nd, nd2)
                cp, cn = ctx_sets[lvl][q["qid"]]
                ip = present_pair(gp, cp)
                idf = present_pair(gp, dp)
                ic = present_pair(gp, idx.c_pair[lvl])
                npd = present_num(gp, dn)
                npc = present_num(gp, idx.c_num[lvl])
                cats[lvl] = categorize(gp, ip, idf, npd, ic, npc)
                flags[lvl] = {"in_ctx": ip, "in_doc": idf, "num_in_doc": npd,
                              "in_corpus": ic, "num_in_corpus": npc, "doc_hits": nd}
            F = flags[PRIMARY]
            ok_by_seed = [bool(next((x.get("ok") for x in rows if x["qid"] == q["qid"]), False)) for rows in per_seed]
            per_q[q["qid"]] = {"qid": q["qid"], "type": q["type"], "part": q.get("part", ""),
                               "gold": q["gold"], "gold_items": gold_repr(gp), "n_gold_items": len(gp),
                               "cat": cats[PRIMARY], "cats": cats, "level_sensitive": len(set(cats.values())) > 1,
                               "n_seeds": len(ok_by_seed), "n_wrong": sum(1 for o in ok_by_seed if not o),
                               "correct_any": any(ok_by_seed), "correct_all": all(ok_by_seed),
                               **{k2: v for k2, v in F.items()}}
            rows_all.append({"group": name, "qid": q["qid"], "type": q["type"], "part": q.get("part", ""),
                             "gold": q["gold"], "gold_items": gold_repr(gp),
                             "category_L4_primary": cats[PRIMARY], "category_L3_line": cats["line"],
                             "category_L1_strict": cats["strict"], "level_sensitive": per_q[q["qid"]]["level_sensitive"],
                             "in_ctx": F["in_ctx"], "in_doc": F["in_doc"], "num_in_doc": F["num_in_doc"],
                             "in_corpus": F["in_corpus"], "doc_name_hits": F["doc_hits"],
                             "n_seeds": per_q[q["qid"]]["n_seeds"], "n_wrong_seeds": per_q[q["qid"]]["n_wrong"],
                             "correct_any_seed": per_q[q["qid"]]["correct_any"], "人工裁决": ""})

        wr = {tag: [c for c in per_q.values() if (c["n_wrong"] == c["n_seeds"] if tag == "all3" else
                  (c["n_wrong"] * 2 >= c["n_seeds"] if tag == "maj" else c["n_wrong"] > 0))]
              for tag in ("any", "all3", "maj")}
        g["n_question"] = len(per_q)
        g["wrong"] = {t: len(v) for t, v in wr.items()}
        g["dist"] = {t: dict(collections.Counter(c["cat"] for c in v)) for t, v in wr.items()}
        g["dist_other_levels"] = {"L1_strict": dict(collections.Counter(c["cats"]["strict"] for c in wr["any"])),
                                  "L3_line": dict(collections.Counter(c["cats"]["line"] for c in wr["any"]))}
        g["n_level_sensitive"] = sum(1 for c in per_q.values() if c["level_sensitive"])
        g["shares_all_questions_pct"] = {}
        for tag, pool in wr.items():
            up = sum(1 for c in pool if c["cat"] in NOT_GEN)
            lo, hi = wilson(up, len(pool)) if pool else (0, 0)
            g.setdefault("upstream", {})[tag] = {
                "count": up, "of_wrong": "%d/%d" % (up, len(pool)),
                "share_of_wrong_pct": round(100 * up / len(pool), 1) if pool else None,
                "wilson95CI_pct": [round(lo, 1), round(hi, 1)],
                "share_of_all_questions_pct": round(100 * up / g["n_question"], 1)}
        for cat in CAT_ORDER:
            cnt = sum(1 for c in wr["all3"] if c["cat"] == cat)
            lo, hi = wilson(cnt, len(wr["all3"]))
            g["shares_all_questions_pct"][cat] = {
                "count_all3": cnt, "share_of_all_questions_pct": round(100 * cnt / g["n_question"], 1),
                "share_of_wrong_all3_pct": round(100 * cnt / len(wr["all3"]), 1) if wr["all3"] else None,
                "wilson95CI_of_wrong_pct": [round(lo, 1), round(hi, 1)]}
        g["ok_but_value_not_in_ctx"] = sum(1 for c in per_q.values() if c["correct_all"] and c["in_ctx"] is False)
        summary["groups"].append(g)
        ctx_by_group[name] = per_q
        d = g["dist"]["all3"]
        print("[ok] %-16s k=%d fid=%.3f 上游丢失(all3)=%s 结构脱钩=%d 真丢失=%d 生成侧=%d" % (
            name, k, fidelity, g["upstream"]["all3"]["of_wrong"], d.get("binding_lost", 0),
            d.get("value_absent", 0), d.get("gen_side", 0)), flush=True)

    # 跨规模不变性（同题配对 McNemar）
    def flag(c, defn, scat):
        isw = (c["n_wrong"] == c["n_seeds"]) if defn == "all3" else (c["n_wrong"] * 2 >= c["n_seeds"])
        return isw and c["cat"] in scat
    for a, b in itertools.combinations([n for n in ctx_by_group if n.startswith("DCU-")], 2):
        for sname, scat in (("上游丢失(除生成侧)", NOT_GEN), ("仅检索漏捞", ("retrieval_miss",)),
                            ("仅结构脱钩 binding_lost", ("binding_lost",))):
            for defn in ("all3", "maj"):
                ia, ib = ctx_by_group[a], ctx_by_group[b]
                common = sorted(set(ia) & set(ib))
                sa = sum(1 for q in common if flag(ia[q], defn, scat))
                sb = sum(1 for q in common if flag(ib[q], defn, scat))
                only_a = sum(1 for q in common if flag(ia[q], defn, scat) and not flag(ib[q], defn, scat))
                only_b = sum(1 for q in common if flag(ib[q], defn, scat) and not flag(ia[q], defn, scat))
                p = mcnemar_exact(only_a, only_b)
                summary["invariance_tests"]["%s vs %s | %s [%s]" % (a, b, sname, defn)] = {
                    "n_paired": len(common), "A": sa, "B": sb,
                    "share_A_pct": round(100 * sa / len(common), 1), "share_B_pct": round(100 * sb / len(common), 1),
                    "discordant": [only_a, only_b], "mcnemar_exact_p": round(p, 4),
                    "verdict": "分辨不出（与「跨规模不变」一致）" if p > 0.05 else "两侧可分辨，「不变」不成立",
                    "interpret": "近似同义反复（类别与模型无关），规模效应看 scale_rescue"}

    # 规模到底救回了哪些题——按失败类别分解（这才是规模效应的正确形态）
    def all3w(c):
        return c["n_wrong"] == c["n_seeds"]
    summary["scale_rescue"] = {}
    for a, b in (("DCU-3B", "DCU-7B"), ("DCU-3B", "DCU-14B"), ("Local-3B-q4", "Local-7B-loose")):
        if a not in ctx_by_group or b not in ctx_by_group:
            continue
        A, B = ctx_by_group[a], ctx_by_group[b]
        common = sorted(set(A) & set(B))
        res, rev = collections.Counter(), collections.Counter()
        for q in common:
            if all3w(A[q]) and not all3w(B[q]):
                res[A[q]["cat"]] += 1
            elif not all3w(A[q]) and all3w(B[q]):
                rev[B[q]["cat"]] += 1
        summary["scale_rescue"]["%s → %s" % (a, b)] = {
            "rescued_total": sum(res.values()), "rescued_by_category": dict(res),
            "regressed_total": sum(rev.values()), "regressed_by_category": dict(rev),
            "net": sum(res.values()) - sum(rev.values()),
            "share_of_rescues_that_were_gen_side_pct": round(
                100 * res["gen_side"] / sum(res.values()), 1) if sum(res.values()) else None}

    n_q = max([g.get("n_question", 0) for g in summary["groups"] if g.get("status") == "ok"] or [0])
    if n_q:
        se = math.sqrt(0.42 * 0.58 / n_q) * 100
        summary["resolution"] = {
            "n_questions_per_model": n_q, "binomial_SE_at_42pct_pp": round(se, 2),
            "single_model_95CI_halfwidth_pp": round(1.96 * se, 1),
            "paired_detectable_diff_pp": round(1.96 * math.sqrt(2) * se, 1),
            "statement": "per-question n=%d 时单模型比例 95%%CI 半宽≈%.1fpp、同题配对可分辨差≈%.1fpp；"
                         "「跨规模纹丝不动」只能写成「差值低于 %.0fpp 时检验不出」，不可写「完全不变」。"
                         % (n_q, 1.96 * se, 1.96 * math.sqrt(2) * se, 1.96 * math.sqrt(2) * se)}

    sens = [r for r in rows_all if r["n_wrong_seeds"] and r["level_sensitive"]]
    picked = sens[:8]
    for cat in ("value_absent", "binding_lost", "collision_elsewhere", "gen_side", "retrieval_miss"):
        extra = [r for r in rows_all if r["n_wrong_seeds"] and r["category_L4_primary"] == cat
                 and not r["level_sensitive"]][:3]
        picked.extend(extra)
    seen, uniq = set(), []
    for r in picked:
        key = (r["group"], r["qid"])
        if key not in seen and len(uniq) < args.spot:
            seen.add(key); uniq.append(r)
    picked = uniq
    summary["spotcheck"] = {"n": len(picked), "n_level_sensitive_total": len(sens),
                            "by_category": dict(collections.Counter(r["category_L4_primary"] for r in picked))}

    cols = list(rows_all[0].keys()) if rows_all else []
    for fn, data in (("taxonomy_per_question.csv", rows_all), ("taxonomy_spotcheck15.csv", picked)):
        with open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for r in data:
                w.writerow({c: r.get(c, "") for c in cols})
    summary["per_question_rows"] = len(rows_all)
    with open(os.path.join(OUT_DIR, "taxonomy_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    print("\n== 产物 ==")
    for fn in ("taxonomy_summary.json", "taxonomy_per_question.csv", "taxonomy_spotcheck15.csv"):
        print("  %s  %d bytes" % (fn, os.path.getsize(os.path.join(OUT_DIR, fn))))
    for g in summary["groups"]:
        if g.get("status") != "ok":
            print("%-16s %s" % (g["group"], g["status"])); continue
        s = g["shares_all_questions_pct"]
        print("%-16s 占全题%%: 生成侧=%.1f 漏捞=%.1f 结构脱钩=%.1f 跨档碰撞=%.1f 真丢失=%.1f | 敏感题=%d 蒙对=%d" % (
            g["group"], s["gen_side"]["share_of_all_questions_pct"], s["retrieval_miss"]["share_of_all_questions_pct"],
            s["binding_lost"]["share_of_all_questions_pct"], s["collision_elsewhere"]["share_of_all_questions_pct"],
            s["value_absent"]["share_of_all_questions_pct"], g["n_level_sensitive"], g["ok_but_value_not_in_ctx"]))


if __name__ == "__main__":
    main()
