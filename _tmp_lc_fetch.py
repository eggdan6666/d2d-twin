import os, re, sys, requests

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.szlcsc.com/",
}
PDF_RE = re.compile(r'https://atta\.szlcsc\.com/upload/public/pdf/source/[^"\'\s<>\\]+\.pdf')

# args: PID|relative_out_path  PID|out2 ...
for arg in sys.argv[1:]:
    pid, out_rel = arg.split("|")
    page = "https://item.szlcsc.com/%s.html" % pid
    try:
        r = requests.get(page, headers=UA, timeout=40)
        t = r.text.replace("\\/", "/")
        pdfs = sorted(set(PDF_RE.findall(t)))
    except Exception as e:
        print("FAIL %s page-error %s" % (out_rel, e))
        continue
    if not pdfs:
        print("FAIL %s no-pdf-link (status %s)" % (out_rel, r.status_code))
        continue
    dest = os.path.join("corpus/data/raw_pdf", out_rel)
    for link in pdfs:
        try:
            d = requests.get(link, headers=UA, timeout=120)
        except Exception as e:
            print("FAIL %s dl-error %s" % (out_rel, e))
            continue
        body = d.content
        if d.status_code != 200 or not body.startswith(b"%PDF-") or len(body) < 20 * 1024:
            print("SKIP %s bad-payload status=%s len=%s head=%r" % (out_rel, d.status_code, len(body), body[:8]))
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(body)
        print("OK %s <- %s (%d bytes)" % (dest, link, len(body)))
        break
    else:
        print("FAIL %s all-links-invalid" % out_rel)
