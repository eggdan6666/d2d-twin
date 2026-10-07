# -*- coding: utf-8 -*-
"""给金标 IR 的保留位段打显式 tier 标记（A/B/C/UNVERIFIED），并修 INA3221 的一处金标错误。

为什么必须做：`is_convention_bit` 原先靠位段**名字/描述**猜"这是不是未文档化的保留位"，
而我写 desc 时对 A 档（文档明说读 0）和 C 档（文档没给访问码）都用了「恒 0」这种措辞 ⇒ 分不开。
后果实测到了两条：
  1) TMP126 的 7 段全是 **R 00h/R 000h/R 00b**（PDF p.26/29/30/31/33 逐位给了 Type），
     却被当成"约定敏感位"——会虚增 ④b；
  2) INA3221 的 6 个告警限值寄存器，手册写的是 `bits 2-0 Reserved **R/W** 0h`（p.31-32），
     我却编成了 RO ⇒ 模型把它们实现成可写（**照手册是对的**）被判失败。
     实测 5/12 份的 ④ 失败信息正是 `CRIT1.UNUSED[2:0] 是 RW 寄存器内的 RO 位：写全 1 后读回 7`。
     ⇒ 这是金标自己的错，属于"我方判据污染分数"，必须改判据而不是记进模型账。

档位定义（写进 IR 的 tier 字段）：
  A = 文档逐位给了访问码且说明读 0            → 计分，且**不受 Q0 影响**
  B = 文档逐位给了访问码且写的是 R/W（哪怕名字叫 Reserved）→ 应编成可写，计分，不受 Q0 影响
  C = 文档没给该位的访问码                    → 唯一受 Q0 裁决影响的档，relax 变体只翻它
  UNVERIFIED = 我还没在 PDF 里定位到逐位 Type 行 → 进 ④u（不计入 ④b），等人工勾选
"""
import sys, os, io, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_setup"))
sys.stdout.reconfigure(encoding="utf-8")

# (芯片, 寄存器名, 位段名) -> (tier, 访问码是否要改, 证据)
FIX = {
    ("INA3221", "CRIT1", "UNUSED"): ("B", "RW", "PDF p.31 Table 8-18：『bits 2-0 Reserved  R/W  0h』——手册标 R/W，可写"),
    ("INA3221", "CRIT2", "UNUSED"): ("B", "RW", "PDF p.31-32 同款表：bits 2-0 Reserved R/W 0h"),
    ("INA3221", "CRIT3", "UNUSED"): ("B", "RW", "PDF p.32 Table 8-25：bits 2-0 Reserved R/W 0h"),
    ("INA3221", "WARN1", "UNUSED"): ("B", "RW", "PDF p.31：Warning-Alert Channel-1 Limit，bits 2-0 Reserved R/W 0h"),
    ("INA3221", "WARN2", "UNUSED"): ("B", "RW", "PDF p.32：bits 2-0 Reserved R/W 0h"),
    ("INA3221", "WARN3", "UNUSED"): ("B", "RW", "PDF p.32：bits 2-0 Reserved R/W 0h"),
    ("INA3221", "SHUNT_SUM_LIMIT", "UNUSED"): ("A", None, "PDF p.33 Table 8-31：『bits 0 Reserved  R  0h』——文档明说读 0"),
    ("INA3221", "PV_UPPER", "UNUSED"): ("A", None, "PDF p.35 Table 8-36：『2-0 Reserved  R  0h』"),
    ("INA3221", "PV_LOWER", "UNUSED"): ("A", None, "PDF p.36 Table 8-38 续表：『2-0 Reserved  R  0h』"),

    ("TMP126", "CONFIG", "RESERVED_15_9"): ("A", None, "PDF p.29 Table 8-8：『15:9 Reserved  R  00h』"),
    ("TMP126", "CONFIG", "RESERVED_6"): ("A", None, "PDF p.29 Figure 8-22 位标注 R-0b"),
    ("TMP126", "ALERT_ENABLE", "RESERVED_15_5"): ("A", None, "PDF p.30 Table 8-9：『15:5 Reserved  R  000h』"),
    ("TMP126", "TLOW_LIMIT", "RESERVED_1_0"): ("A", None, "PDF p.31 Table 8-10：『1:0 Reserved  R  00b』＋原文 always read 00b"),
    ("TMP126", "THIGH_LIMIT", "RESERVED_1_0"): ("A", None, "PDF p.31 Table 8-11：同上"),
    ("TMP126", "SLEW_LIMIT", "RESERVED_15"): ("A", None, "PDF p.33 Table 8-13：『15 Reserved  R  00b』"),
    ("TMP126", "SLEW_LIMIT", "RESERVED_1_0"): ("A", None, "PDF p.33 Table 8-13：『1:0 Reserved  R  00b』"),
}
UNVERIFIED = {
    "TMP102": "PDF p.8 只写了『The unused bits in the temperature register always read 0』（仅覆盖温度寄存器），"
              "CONFIG/TLOW/THIGH 的 [3:0] 未在文本层找到逐位 Type 行",
    "TMP100": "PDF p.9 只写了温度寄存器『unused LSBs set to zero』，TLOW/THIGH 的 [6:0] 未定位到 Type 行",
    "BME280": "Bosch 手册的 ctrl_hum 位表在文本层里没给出 7:3 的 Access 列（解析/排版丢失），需人眼",
    "TMP117": "位标注在 Figure 里（文本层无 R-0b 命中）；这颗本身就是图/表矛盾的那颗（Soft_Reset 位）",
    "LM83": "PDF p.14 命中的是地址级 Reserved（保留地址段），不是 CONFIG 内部位级的 Type",
    "HDC2021": "PDF p.25 的 Interrupt Enable 位表只给了『2 RES 0 Reserved』这样没有访问码列的行 ⇒ 倾向 C 档，但未定稿",
}


def main():
    changed = []
    for part in set(k[0] for k in FIX) | set(UNVERIFIED):
        p = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
        if not os.path.exists(p):
            continue
        ir = json.load(io.open(p, encoding="utf-8"))
        n = 0
        for r in ir["registers"]:
            for f in r.get("fields", []):
                key = (part, r["name"], f["name"])
                if key in FIX:
                    tier, newacc, ev = FIX[key]
                    f["tier"] = tier
                    f["tier_evidence"] = ev
                    if newacc and f.get("access") != newacc:
                        f["access"] = newacc
                        f["desc"] = "[金标纠正 %s] %s | 原编码 %s → %s：%s" % (
                            tier, str(f.get("desc", ""))[:60], "RO", newacc, ev)
                        changed.append("%s.%s[%s] RO→%s" % (part, r["name"], f["bits"], newacc))
                    n += 1
                elif part in UNVERIFIED and f.get("access") == "RO" and re.search(
                        r"UNUSED|RESERVED|_RES\b|^RES\d*$", str(f.get("name", "")), re.I):
                    f["tier"] = "UNVERIFIED"
                    f["tier_evidence"] = UNVERIFIED[part]
                    n += 1
        io.open(p, "w", encoding="utf-8").write(json.dumps(ir, ensure_ascii=False, indent=1))
        print("%-9s 已标 tier 的保留位段 %d 个" % (part, n))
    print("\n金标纠正（访问码改了）：", changed or "无")


if __name__ == "__main__":
    main()
