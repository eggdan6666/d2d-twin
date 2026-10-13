"""Read-only source extraction and baseline; writes only to this new audit directory."""
from pathlib import Path
import json, hashlib, fitz, collections

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'eval/protocol_v2_20261012'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def dump(p, data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inputs=['REPORT.md','SOURCE_POLICY_REVIEW.md','LEGAL_DOMAIN_SUPPLEMENT.md','INDEPENDENT_REPAIR_REVIEW.md','source_policy.json','field_policy_inventory.json','protocol_manifest.json']
dump(OUT/'input_fingerprints.json', {x:sha(BASE/x) for x in inputs})
inventory=json.loads((BASE/'field_policy_inventory.json').read_text(encoding='utf-8'))
chips=sorted({x['chip'] for x in inventory})
pdfs={p.stem.upper():p for p in (ROOT/'corpus/data/raw_pdf').rglob('*.pdf')}
sources={}
for chip in chips:
    p=pdfs[chip.upper()]
    doc=fitz.open(p)
    pages=[]
    for i,page in enumerate(doc):
        s=page.get_text(sort=True)
        pages.append({'pdf_page':i+1,'text':s})
        dest=OUT/'source_extracts'/chip/f'p{i+1:03d}.txt'
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(s,encoding='utf-8')
    dump(OUT/'source_extracts'/chip/'pages.json',pages)
    sources[chip]={'device':chip,'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'pdf_pages':len(doc),'version_first_page_text':pages[0]['text']}
    ir=json.loads((BASE/'ir'/f'{chip}_gold_ir.json').read_text(encoding='utf-8'))
    dump(OUT/'review_inputs'/f'{chip}.json',{'chip':chip,'source':sources[chip],'ir':ir,'prior_policy':json.loads((BASE/'source_policy.json').read_text(encoding='utf-8')).get('chips',{}).get(chip,{}),'inventory':[x for x in inventory if x['chip']==chip]})
    rows=[]
    for reg in ir['registers']:
        rows.append(f"REGISTER {reg['name']} @ {reg.get('addr')} reset={reg.get('reset')} access={reg.get('access')} runtime={reg.get('runtime_value')} DESC={reg.get('desc','')}")
        for f in reg.get('fields',[]): rows.append(f"  {f['name']}[{f['bits']}] {f.get('access')} reset={f.get('reset')} read_as={f.get('read_as')} read_action={f.get('read_action')} tier={f.get('tier')} DESC={f.get('desc','')}")
    (OUT/'review_inputs'/f'{chip}.txt').write_text('\n'.join(rows),encoding='utf-8')
dump(OUT/'source_manifest.json',sources)
protected=set((ROOT/'d2d/ir').rglob('*'))
protected.update(ROOT.rglob('test_d2d_blackbox.py'))
protected.update(BASE.rglob('*'))
for p in (ROOT/'eval').rglob('*'):
    if OUT in p.parents: continue
    if p.is_file() and (any(x in p.name.lower() for x in ['model_results','model_summary','summary','results']) or any('model_comparison' in part for part in p.parts)):
        protected.add(p)
protected={p for p in protected if p.is_file()}
dump(OUT/'protected_files_before.json',{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(protected)})
print(json.dumps({'chips':len(chips),'fields':len(inventory),'per_chip':dict(collections.Counter(x['chip'] for x in inventory)),'protected_files':len(protected),'directory':str(OUT)},ensure_ascii=False))
