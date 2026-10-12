"""Read-only result validation and export; run with the HPC system Python."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path('/public/home/lct3086708928/d2d')
EXPECTED = {(seed, i) for seed in (1, 2, 3) for i in range(4)}
rows, files = [], []
for ir in sorted((ROOT / 'ir').glob('*_gold_ir.json')):
    chip = ir.name.removesuffix('_gold_ir.json')
    result = ROOT / 'eval' / ('results_gen_qwen14b_' + chip.lower() + '.json')
    row = {'chip': chip, 'status': 'MISSING'}
    files.append(ir)
    if result.is_file():
        files.append(result)
        try:
            data = json.loads(result.read_text(encoding='utf-8'))
            pairs = {(r['seed'], r['i']) for r in data}
            fields_ok = all(all(k in r for k in ('rc', 'passed', 'tail', 'code_extracted', 'code')) for r in data)
            complete = len(data) == 12 and pairs == EXPECTED and fields_ok
            row.update(status='COMPLETE' if complete else 'INCOMPLETE',
                       samples=len(data), green=sum(r.get('rc') == 0 for r in data))
        except Exception as exc:
            row.update(status='INVALID', error=str(exc))
    rows.append(row)
    print(json.dumps(row, ensure_ascii=True))
for name in ('eval/test_d2d_blackbox.py', 'eval/gen_code.py', 'rtl/base_sensor.py'):
    p = ROOT / name
    if p.is_file():
        files.append(p)
manifest = {'source': str(ROOT), 'results': rows,
            'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
target = Path.cwd() / 'D2D_QWEN14B_RESULTS.zip'
with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, arcname=str(p.relative_to(ROOT)))
    z.writestr('export_manifest.json', json.dumps(manifest, indent=2, ensure_ascii=True))
print('COMPLETE_CHIPS', sum(r['status'] == 'COMPLETE' for r in rows), 'OF', len(rows))
print('ARCHIVE', str(target))
