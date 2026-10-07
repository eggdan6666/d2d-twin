# -*- coding: utf-8 -*-
"""批量下载 Datasheet PDF（curl 引擎，绕过部分厂商的 TLS 反爬）。
用法: python download.py [--workers N]
已存在的文件自动跳过，可反复运行增量补齐。"""
import sys, os, json, csv, argparse, subprocess, tempfile
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw_pdf")
LOG = os.path.join(HERE, "..", "logs")
MIN_SIZE = 20_000
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def curl_ok(url, tmp):
    r = subprocess.run(
        ["curl", "-s", "-o", tmp, "-w", "%{http_code}",
         "-A", UA, "-H", "Accept: application/pdf,*/*",
         "--max-time", "40", "-L", url],
        capture_output=True, text=True)
    code = r.stdout.strip()
    if code != "200" or not os.path.isfile(tmp) or os.path.getsize(tmp) < MIN_SIZE:
        return False
    with open(tmp, "rb") as f:
        return f.read(5) == b"%PDF-"

def fetch(entry):
    part = entry["part"]
    folder = os.path.join(RAW, entry["manufacturer"])
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, part + ".pdf")
    if os.path.isfile(dest) and os.path.getsize(dest) >= MIN_SIZE:
        return {"part": part, "status": "skip_exists", "url": None,
                "bytes": os.path.getsize(dest)}
    fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=folder)
    os.close(fd)
    try:
        for url in entry["urls"]:
            if curl_ok(url, tmp):
                size = os.path.getsize(tmp)
                os.replace(tmp, dest)
                tmp = None
                return {"part": part, "status": "ok", "url": url, "bytes": size}
    finally:
        if tmp and os.path.isfile(tmp):
            os.remove(tmp)
    return {"part": part, "status": "failed", "url": entry["urls"][0], "bytes": 0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    sys.path.insert(0, HERE)
    from manifest import build_entries
    entries = build_entries()
    print(f"清单共 {len(entries)} 个型号")
    from concurrent.futures import ThreadPoolExecutor
    results = []
    def safe(e):
        try:
            return fetch(e)
        except Exception as ex:
            return {"part": e["part"], "status": "failed",
                    "url": str(ex)[:100], "bytes": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(safe, entries):
            results.append(r)
            print(f"[{r['status']:>11}] {r['part']}")
    ok = [r for r in results if r["status"] in ("ok", "skip_exists")]
    failed = [r for r in results if r["status"] == "failed"]
    os.makedirs(LOG, exist_ok=True)
    with open(os.path.join(LOG, "download_result.jsonl"), "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(LOG, "needs_manual.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["part", "manufacturer", "首个候选URL", "建议"])
        e = {x["part"]: x for x in entries}
        for r in failed:
            x = e[r["part"]]
            w.writerow([x["part"], x["manufacturer"], x["urls"][0], "官网检索页手动下载"])
    print(f"\n完成：成功 {len(ok)} / 失败 {len(failed)} / 总计 {len(results)}")

if __name__ == "__main__":
    main()
