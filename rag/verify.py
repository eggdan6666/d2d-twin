# -*- coding: utf-8 -*-
"""跨文档答案归属校验器（编排层·答案校验环节）。
原理: 上下文按型号分块; 答案中"型号 X 的值 V"须能在 X 自己的块里找到 V,
      若 V 只出现在别的型号块里 → 判为归属错位(swap), 交编排层重答或升级模型。"""
from __future__ import annotations
import re

NUM = r"[-−+]?\d+(?:\.\d+)?"

def split_by_part(ctx: str):
    """context_for_parts 的产物按 '[PART §sec]' 头分组."""
    groups = {}
    for block in ctx.split("\n\n---\n\n"):
        m = re.match(r"\[([\w\-.]+) §", block)
        if m:
            groups.setdefault(m.group(1).upper(), []).append(block)
    return {k: "\n".join(v) for k, v in groups.items()}

def _nums(text: str):
    return set(re.findall(NUM, text.replace("−", "-").replace(" ", "")))

def extract_claims(answer: str, parts):
    """型号锚点后取窗口, 窗口截止于下一个型号锚点, 并剔除其他型号名防其内部数字串扰."""
    claims = []
    up = answer.upper()
    anchors = sorted((up.find(p.upper()), p) for p in parts if up.find(p.upper()) >= 0)
    for ai, (pos, p) in enumerate(anchors):
        end = anchors[ai + 1][0] if ai + 1 < len(anchors) else len(answer)
        win = answer[pos + len(p): min(end, pos + len(p) + 160)]
        for other in parts:
            win = re.sub(re.escape(other), " ", win, flags=re.I)
        for n in re.findall(NUM, win):
            claims.append((p.upper(), n))
    return claims

def check_attribution(answer: str, ctx: str, doc_texts: dict | None = None):
    """doc_texts: {PART大写: 该型号全文档文本}。给了就把校验域从 ctx 块扩到全文档,
    消除"引用同文档其他行"型误报。"""
    groups = split_by_part(ctx)
    if len(groups) < 2:
        return {"ok": True, "skipped": "single-doc context", "errors": []}
    all_nums = {}
    for k, v in groups.items():
        src = (doc_texts or {}).get(k, v)
        all_nums[k] = _nums(src)
    errors = []
    for part, num in extract_claims(answer, list(groups)):
        n = num.replace(" ", "")
        n_strip = n.lstrip("+")
        if n in all_nums[part] or n_strip in all_nums[part] or n.lstrip("-") in all_nums[part]:
            continue
        wrong = [q for q in all_nums if n in all_nums[q] or n_strip in all_nums[q]]
        if wrong:
            errors.append({"part": part, "value": num, "actually_from": wrong[0]})
        # 数值哪都没有=纯幻觉, 也记错(但可能是单位换算, 保守只标 swap)
    return {"ok": not errors, "errors": errors,
            "retry_hint": ("You swapped values between parts. Re-answer: "
                           + "; ".join(f"{e['value']} belongs to {e['actually_from']}, not {e['part']}"
                                       for e in errors[:4]))}

if __name__ == "__main__":
    # 单元自测: X001 型病例
    ctx = ("[TMP1075 §elec_chars]\nInput voltage range 1.7 V to 5.5 V\n\n---\n\n"
           "[BME280 §front]\nSupply voltage 1.71 V to 3.6 V")
    bad = "TMP1075 supply is 1.71 V to 3.6 V, BME280 is 1.7 V to 5.5 V."
    good = "TMP1075: 1.7 V to 5.5 V; BME280: 1.71 V to 3.6 V."
    r1, r2 = check_attribution(bad, ctx), check_attribution(good, ctx)
    print("错位答案 →", r1)
    print("正确答案 →", r2)
    assert not r1["ok"] and r2["ok"], "自测未通过"
    print("PASS: swap 检出、正答放行")
