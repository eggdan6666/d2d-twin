# -*- coding: utf-8 -*-
"""B: 用已核验的 param 题重建 cross 集(题面携带精确行标签), 输出 datasheet_qa100_v3.json.
cross 的两侧值与参数名直接取自 param 题, 消除"同一参数名对应多表行"的歧义."""
import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

def key(p):
    return re.sub(r"[^a-z0-9 ]", "", p.lower()).strip()

ds = json.load(open(os.path.join(HERE, "datasheet_qa100_v2.json"), encoding="utf-8"))
params = [q for q in ds if q["type"] == "param"]
for q in params:
    m = re.search(r"of ([\w\-.]+) \(", q["question"])
    q["part"] = m.group(1) if m else ""
bykey = {}
for q in params:
    m = re.search(r"for '([^']+)'", q["question"])
    if not m:
        continue
    bykey.setdefault(key(m.group(1)) + "|" + m.group(1).lower()[:6], []).append((m.group(1), q))

cross, used = [], set()
seen_pairs = set()
for grp in bykey.values():
    rows = [x for x in grp]
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            (p1, a), (p2, b) = rows[i], rows[j]
            if a["part"].upper() == b["part"].upper():
                continue
            pk = (a["qid"], b["qid"])
            if pk in seen_pairs:
                continue
            seen_pairs.add(pk)
            cross.append({
                "qid": f"X{len(cross):03d}", "type": "cross",
                "question": (f"For the datasheet parameter '{p1}', which part specifies the larger "
                             f"value: {a['part']} or {b['part']}? Give both values with units."),
                "gold": f"{a['part']}:{a['gold']}|{b['part']}:{b['gold']}",
                "evidence": a.get("evidence", "") + " || " + b.get("evidence", ""),
                "note": f"rebuilt from verified param pair {a['qid']}+{b['qid']}"})
            used.update(a["qid"], b["qid"]) if False else used.update([a["qid"], b["qid"]])
ds3 = params + cross
# --- 追加: 旧 C 题面重写(用池子里的精确行标签替换泛化 canon 名) ---
pool = json.load(open(os.path.join(HERE, "drafts_param.json"), encoding="utf-8"))
idx = {}
for x in pool:
    idx.setdefault((x["part"].upper(), x["gold"].lower().replace(" ", "")), x["param"])
    nums = set(re.findall(r"\d+(?:\.\d+)?", x["gold"]))
    if nums:
        idx.setdefault((x["part"].upper(), "N" + "".join(sorted(nums))), x["param"])

def lookup(part, val):
    v = val.lower().replace(" ", "")
    if (part.upper(), v) in idx:
        return idx[(part.upper(), v)]
    nums = "".join(sorted(set(re.findall(r"\d+(?:\.\d+)?", val))))
    return idx.get((part.upper(), "N" + nums))

old_ds = json.load(open(os.path.join(HERE, "datasheet_qa100_v2.json"), encoding="utf-8"))
rewritten = kept = 0
for q in old_ds:
    if q["type"] != "cross":
        continue
    segs = [tuple(s.split(":", 1)) for s in q["gold"].split("|") if ":" in s]
    la = lookup(segs[0][0], segs[0][1]) if len(segs) == 2 else None
    lb = lookup(segs[1][0], segs[1][1]) if len(segs) == 2 else None
    old_label = re.search(r"For '([^']+)'", q["question"])
    old_label = old_label.group(1) if old_label else "parameter"
    if la and lb and (la != old_label or lb != old_label):
        q2 = dict(q)
        if la == lb:
            q2["question"] = (f"For the datasheet parameter '{la}', which part specifies the larger "
                             f"value: {segs[0][0]} or {segs[1][0]}? Give both values with units.")
        else:
            q2["question"] = (f"Compare the datasheet-specified values '{la}' ({segs[0][0]}) vs "
                             f"'{lb}' ({segs[1][0]}) — which is larger? Give both values with units.")
        q2["note"] = (q.get("note", "") + "|question disambiguated").strip("|")
        ds3.append(q2)
        rewritten += 1
    else:
        ds3.append(q)
        kept += 1
json.dump(ds3, open(os.path.join(HERE, "datasheet_qa100_v3.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
ncross = sum(1 for x in ds3 if x["type"] == "cross")
print(f"param {len(params)} + cross {ncross} (新配对{len(cross)} + 重写{rewritten} + 原样{kept}) = {len(ds3)} 题 → v3")
for c in cross[:4]:
    print(" ", c["qid"], c["question"][:86], "| gold:", c["gold"][:44])
if ncross < 20:
    print("!! cross 不足20题, 需从 draft 池补配对(报告注明)")
