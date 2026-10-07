# -*- coding: utf-8 -*-
"""交付打包: 生成 delivery/ 目录 + zip(不含456个PDF原件, 含清单)."""
import sys, os, json, zipfile, shutil, time
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
D = "delivery"
os.makedirs(D, exist_ok=True)

def cp(src_dir, dst_dir, filt=lambda f: f.endswith((".json", ".jsonl", ".md", ".csv", ".py", ".png"))):
    os.makedirs(dst_dir, exist_ok=True)
    n = 0
    for f in os.listdir(src_dir):
        p = os.path.join(src_dir, f)
        if os.path.isfile(p) and filt(f):
            shutil.copy2(p, os.path.join(dst_dir, f)); n += 1
    return n

cnt = {}
cnt["qa100"] = cp("eval/qa100", f"{D}/qa100")
cnt["results"] = cp("eval", f"{D}/results")
os.makedirs(f"{D}/code", exist_ok=True)
for src, dst in (("rag", f"{D}/code/rag"), ("corpus/scripts", f"{D}/code/corpus_scripts")):
    cnt[src] = cp(src, dst)
shutil.copy2("eval/run_longmemeval.py", f"{D}/code/run_longmemeval.py")

# 语料: 索引+统计+切片/全文打包(文本类, 不含PDF)
os.makedirs(f"{D}/corpus", exist_ok=True)
shutil.copy2("corpus/data/index/corpus_index.jsonl", f"{D}/corpus/corpus_index.jsonl")
shutil.copy2("corpus/data/index/corpus_stats.json", f"{D}/corpus/corpus_stats.json")
pdfs = []
for root, _, fs in os.walk("corpus/data/raw_pdf"):
    for f in fs:
        if f.endswith(".pdf"):
            pdfs.append({"path": os.path.relpath(os.path.join(root, f), "."),
                         "bytes": os.path.getsize(os.path.join(root, f))})
json.dump(pdfs, open(f"{D}/corpus/raw_pdf_manifest.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

stamp = time.strftime("%Y%m%d")
zipname = f"HD-Agent_delivery_{stamp}.zip"
with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
    for base in ("delivery",):
        for root, _, fs in os.walk(base):
            for f in fs:
                if f.endswith(".zip"):
                    continue
                p = os.path.join(root, f)
                z.write(p)
    for d in ("corpus/data/chunks", "corpus/data/parsed"):
        for root, _, fs in os.walk(d):
            for f in fs:
                z.write(os.path.join(root, f))
    for f in ("eval/results",):
        pass
size_mb = os.path.getsize(zipname) / 1e6
summary = {"copied": cnt, "zip": zipname, "zip_mb": round(size_mb, 1),
           "pdf_count": len(pdfs), "pdf_total_gb": round(sum(p['bytes'] for p in pdfs)/1e9, 2)}
json.dump(summary, open(f"{D}/package_summary.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
