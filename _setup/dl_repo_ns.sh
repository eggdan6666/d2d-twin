#!/bin/sh
# usage: dl_repo_ns.sh <namespace/model-name>   例如 deepseek-ai/deepseek-coder-6.7b-instruct
# dl_repo.sh 把命名空间硬编码成 Qwen，换厂商时必须带命名空间，故另写一份。
R="$1"
export http_proxy='http://preset:6e298f07@10.16.1.51:3128'
export https_proxy='http://preset:6e298f07@10.16.1.51:3128'
export no_proxy='localhost,127.0.0.1'
export PATH=/opt/conda/bin:$PATH
B=$(basename "$R")
D="/root/private_data/models/$B"
mkdir -p "$D" && cd "$D" || exit 1
curl -s "https://modelscope.cn/api/v1/models/$R/repo/files?Recursive=true" > "/root/ms_files_$B.json"
python3 - "$B" <<'PY'
import json, sys
b = sys.argv[1]
d = json.load(open(f'/root/ms_files_{b}.json'))
with open(f'/root/dl_list_{b}.txt', 'w') as f:
    for x in d['Data']['Files']:
        if not x['Path'].endswith('.gitattributes'):
            f.write(x['Path'] + '\n')
PY
grep -c . "/root/dl_list_$B.txt" || exit 1
xargs -P4 -I{} sh -c "wget -q -c 'https://modelscope.cn/models/$R/resolve/master/{}' -O '{}' && echo 'OK {}'" < "/root/dl_list_$B.txt"
echo "DOWNLOAD_PHASE_DONE $B"
python3 - "$B" <<'PY'
import json, sys, os
b = sys.argv[1]
d = json.load(open(f'/root/ms_files_{b}.json'))
bad = 0
tot = 0
for x in d['Data']['Files']:
    p = x['Path']
    if p.endswith('.gitattributes'):
        continue
    want, have = x.get('Size', 0), (os.path.getsize(p) if os.path.exists(p) else -1)
    tot += want
    if have != want:
        bad += 1
        print('MISMATCH', p, want, have)
print('VERIFY %s bytes=%d files_bad=%d' % (b, tot, bad))
PY
