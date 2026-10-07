# -*- coding: utf-8 -*-
"""从 typ_app 切片自动草拟应用电路题 → 审校表 review_app*.csv。
自动题一律 note=auto-draft-needs-review，需人工审校后方可用于正式结论。
合并进 datasheet_qa100_v4.json 需显式 --write-v4（v4 已定稿，防止重跑静默改写历史交付物）。"""
import sys, os, json, re, random, csv, argparse
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
from rag.corpus import load_chunks

# 三条规则各自的必要性（缺一会复现对应缺陷，第一轮人工审校 30 题实测）：
# 1) 左右边界：无边界时 C\d{1,2} 命中型号串内部(UCC28951→'C28'+尾巴'951 A'、L324A→'L32'、
#    图号 C002→'C00')，那一轮 16/30 题因此作废。
# 2) 单位白名单只收元件值(F/Ω/H)，不含 V/mA/A/kHz：位号后紧跟的 "3.3V"、"2.5A" 是原理图的
#    节点电压/电流标签而非该元件取值(DRV8312 R44、LM5021 R23 实测如此)；顺带灭掉型号尾巴。
# 3) 间隙允许换行：PDF 竖排图注里 "C15\n10 nF" 是真配对(AMC1400 实测)，禁跨行会把候选池
#    从 94 组压到 18 组；跨行带来的假配对由规则 2 拦。
COMP = re.compile(
    r"(?<![A-Za-z0-9/])((?:external|output|feedback|timing|boot|catch|snubber|decoupling|bulk|input)"
    r"[\w \-]{0,22}?(?:capacitor|resistor|inductor|diode|network|divider)"
    r"|C\d{1,2}|R\d{1,2}|L\d{1,2})(?![0-9A-Za-z])"
    r"[^A-Za-z0-9]{0,25}(\d+(?:\.\d+)?\s*(?:pF|nF|[uµ]F|k?[Mm]?Ω|mH|[uµ]H)\b)", re.I)

# 规则4：位号类型必须与单位一致。图注/PDF 文本流里位号与值会串行错配，实测产出的假配对
# 全是这一类：LM5023 'R17'→100pF(电阻挂电容值)、UCC28180 'C10'→327 µH、UCC28910 'R10'→6.8μF、
# UCC29950 'R56'→470pF —— 单位反类型即判错，不需要人工。
KIND_UNIT = ((re.compile(r"^C\d", re.I), re.compile(r"[uµmnp]?F$", re.I)),
             (re.compile(r"^R\d", re.I), re.compile(r"Ω$", re.I)),
             (re.compile(r"^L\d", re.I), re.compile(r"[uµm]?H$", re.I)))
WORD_KIND = (("capacitor", re.compile(r"[uµmnp]?F$", re.I)),
             ("resistor", re.compile(r"Ω$", re.I)),
             ("inductor", re.compile(r"[uµm]?H$", re.I)))

def type_ok(item, val):
    u = val.strip()
    for rx, urx in KIND_UNIT:
        if rx.match(item):
            return bool(urx.search(u))
    for w, urx in WORD_KIND:
        if w in item.lower():
            return bool(urx.search(u))
    return True                                    # diode/network 等不约束

def gap_ok(gap):
    """规则6：位号与值之间的文本若同时含左右括号(或方括号)，说明这段跨过了一个完整
    表达式边界，值属于括号里的另一项。实测假配对 OPA462 'R13'→100 kΩ 的 gap 就是 ") = ("
    (原文 R12 = (R11 – R13) = (100 kΩ– 125 Ω))，而真赋值 "R15 = 100 kΩ"、"capacitor (≥ 1000 µf)"
    的 gap 只含单侧括号或纯赋值号。"""
    return not (("(" in gap and ")" in gap) or ("[" in gap and "]" in gap))

def ev_fp(t):
    """证据文本指纹：字符 5-gram 集合。同族文档复制同一张图注时指纹高度重合，
    而 (位号,值) 相同但电路不同的巧合不会——批次三实测 A240(LM5160 C13 0.01µF) 与
    A205(LM5023 C13 0.01µF) 被旧键误判成簇，人工救回 1 题。"""
    s = re.sub(r"\W+", "", (t or "").lower())
    return {s[i:i + 5] for i in range(0, max(0, len(s) - 4))}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=30)
    ap.add_argument("--qid-start", type=int, default=0, help="新批次从 100 起可避免与已审校批次撞 qid")
    ap.add_argument("--per-doc", type=int, default=2, help="每份文档最多出几题(旁路电容组会刷同值题)")
    ap.add_argument("--sections", default="typ_app",
                    help="逗号分隔的取证章节。typ_app 用原题干；扩到其他章节必须换 --stem，"
                         "否则题干与证据章节不符(口径漂移)")
    ap.add_argument("--stem", default=None,
                    help='题干模板，含 {part}/{mfr}/{item}；缺省为 typ_app 原句')
    ap.add_argument("--review-out", default="review_app.csv")
    ap.add_argument("--exclude-review", nargs="*", default=[],
                    help="已审校批次的 csv(可多个)：同 (型号, 位号) 组合不再重复出候选")
    ap.add_argument("--write-v4", action="store_true")
    a = ap.parse_args()
    stem = a.stem or "In the typical application circuit of {part} ({mfr}), what value is specified for the '{item}'?"
    for need in ("{part}", "{item}"):
        if need not in stem:
            sys.exit(f"--stem 缺占位符 {need}")
    secs = {s.strip() for s in a.sections.split(",") if s.strip()}
    if (secs - {"typ_app"}) and a.stem is None:
        sys.exit("取证章节含 typ_app 以外的内容时必须显式给 --stem，否则题干与证据不符")
    excluded = set()
    for fn in a.exclude_review:
        import io as _io
        for r in csv.DictReader(_io.StringIO(
                open(os.path.join(HERE, fn), "rb").read().decode("utf-8-sig"))):
            mt = re.search(r"circuit of (\S+)", r["question"]) or re.search(r"guidance for (\S+)", r["question"])
            mi = re.search(r"for the '([^']+)'", r["question"])
            if mt and mi:
                excluded.add((mt.group(1).lower(), mi.group(1).lower()))
    chunks = load_chunks()
    apps = [c for c in chunks if c.section in secs and len(c.text) > 800]
    bypart = {}
    for c in apps:
        bypart.setdefault(c.doc_id, []).append(c)
    random.seed(42)
    docs = list(bypart.values())
    random.shuffle(docs)
    drafts = []
    for cs in docs:
        if len(drafts) >= a.target:
            break
        seen, got = set(), 0
        for c in sorted(cs, key=lambda x: -len(x.text)):
            if got >= a.per_doc:
                break
            for m in COMP.finditer(c.text):
                item, val = m.group(1).strip(), m.group(2).strip()
                key = (c.doc_id, item.lower()[:14])
                if key in seen or len(item) < 3 or item.lower().startswith(("r ", "c ")):
                    continue
                if (c.part.lower(), item.lower()) in excluded:
                    continue
                if not type_ok(item, val):
                    continue
                if not gap_ok(c.text[m.end(1):m.start(2)]):
                    continue
                if re.search(r"(\w+)\s+\1", item, re.I):
                    continue                             # "Bulk Capacitor Capacitor" 型表格转储重词
                seen.add(key)
                sent = c.text[max(0, m.start() - 90):m.end() + 40].replace("\n", " ")
                hint = ""
                if "|" in c.text[m.start():m.end()] or "---" in sent:
                    hint = " | 疑:表格竖线落在位号与值之间,值归属需人工确认"
                elif re.search(r"=\s*[\d.]", sent) and sent.lower().count(item.lower()) > 1:
                    hint = " | 疑:证据是设计计算式,同段有多个同类位号,值易错配"
                drafts.append({
                    "qid": f"A{a.qid_start + len(drafts):03d}", "type": "app",
                    "question": stem.format(part=c.part, mfr=c.manufacturer, item=item),
                    "gold": val, "evidence": sent[:180], "part": c.part, "item": item,
                    "section": c.section,
                    "note": (f"auto-draft-needs-review | gap={m.start(2) - m.end(1)}"
                             f" | 源章节={c.section}"
                             + ("(非typ_app,题干已换口径)" if c.section != "typ_app" else "")
                             + hint)})
                got += 1
                if got >= a.per_doc or len(drafts) >= a.target:
                    break
    # 冗余簇标记：按证据文本指纹(Jaccard≥0.5)聚，而不是按 (位号,值) 巧合——
    # 同族文档整段复制同一张图注才算冗余，不同电路里的同名元件各算一道有效题。
    fps = [ev_fp(d["evidence"]) for d in drafts]
    par = list(range(len(drafts)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    for i in range(len(drafts)):
        for j in range(i + 1, len(drafts)):
            if not fps[i] or not fps[j]:
                continue
            u = len(fps[i] | fps[j])
            if u and len(fps[i] & fps[j]) / u >= 0.5:
                par[find(i)] = find(j)
    grp = {}
    for i in range(len(drafts)):
        grp.setdefault(find(i), []).append(i)
    for members in grp.values():
        if len(members) < 2:
            continue
        head = drafts[members[0]]["qid"]
        for n, i in enumerate(members):
            d = drafts[i]
            tag = f" | 同图注簇×{len(members)}(首道 {head})"
            d["note"] += tag + ("｜簇代表,留这道" if n == 0 else "｜簇内复制题,整簇只留首道时填 drop")
    json.dump(drafts, open(os.path.join(HERE, a.review_out.replace(".csv", ".json")),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.write_v4:
        v3 = json.load(open(os.path.join(HERE, "datasheet_qa100_v3.json"), encoding="utf-8"))
        v4 = v3 + drafts
        json.dump(v4, open(os.path.join(HERE, "datasheet_qa100_v4.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, a.review_out), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "question", "gold", "evidence", "verdict(ok/edit/drop)", "note"])
        for d in drafts:
            w.writerow([d["qid"], d["question"], d["gold"], d["evidence"], "", d["note"]])
    print(f"app 草稿 {len(drafts)} 题 → 审校表 {a.review_out}"
          f"{' + 已写 v4' if a.write_v4 else ''}")
    print(f"取证章节={sorted(secs)} | 题干={'(原 typ_app 句)' if a.stem is None else a.stem[:48]}")
    print("草稿:", len(drafts), "| 涉及型号:", len({d["part"] for d in drafts}),
          "| 独立(位号,值)配对:", len({(d["item"].lower(), d["gold"].lower()) for d in drafts}),
          "| 带同图注簇标记:", sum(1 for d in drafts if "同图注簇" in d["note"]))

if __name__ == "__main__":
    main()
