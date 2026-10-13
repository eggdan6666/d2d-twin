"""Execute bounded semantic scenarios and package an explicit non-admission gate."""
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/semantic_protocol_v3_20261012'
sys.path.insert(0, str(OUT))
from compiler import compile_ledger, production_gate, sha, verified_inputs
from scenarios import SCENARIOS


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    started = time.monotonic()
    rows, bundle = verified_inputs()
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in
              [OUT/'runtime.py', OUT/'compiler.py', OUT/'scenarios.py', Path(__file__),
               OUT.parent/'independent_source_admission_20261012/audit_bundle_manifest.json']}
    execution = {}
    for name, function in SCENARIOS.items():
        device, checks = function()
        assert checks.records, name
        execution[name] = {'status': 'PASS', 'assertions': len(checks.records),
                           'checks': checks.records, 'trace': device.trace}
    ledger = compile_ledger(rows, execution)
    write('scenario_execution.json', execution)
    write('repair_closure_ledger.json', ledger)
    write('admission_gate.json', production_gate(rows, ledger))
    demonstrated = {r['inventory_field_id']: [x for x in ledger
                    if x['inventory_field_id'] == r['inventory_field_id'] and x['executed_clauses']]
                    for r in rows if r['overall_status'] == 'REPAIR'}
    queue = [{'inventory_field_id': r['inventory_field_id'], 'chip': r['chip'],
              'register': r['register'], 'field': r['field'], 'source_verdict': 'REPAIR',
              'integration_status': 'OPEN', 'partial_demonstrations': demonstrated[r['inventory_field_id']],
              'repair_dimensions': {k:v for k,v in r['dimensions'].items() if v['status']=='REPAIR'}}
             for r in rows if r['overall_status']=='REPAIR']
    queue.sort(key=lambda r: (r['chip'] != 'TMP117', r['chip'], r['inventory_field_id']))
    write('remaining_repair_queue.json', queue)
    for relative, expected in inputs.items():
        assert sha(ROOT/relative) == expected
    write('execution_manifest.json', {'protocol': '3.0-semantic-prototype-20261012.1',
         'execution_date_client': '2026-10-13',
         'status': 'BOUNDED_EXECUTED_NOT_PRODUCTION_ADMITTED', 'python': platform.python_version(),
         'command': 'python _setup/build_semantic_v3.py', 'elapsed_seconds': time.monotonic()-started,
         'input_sha256': inputs, 'source_bundle_files_verified': len(bundle['files']),
         'source_pdfs_verified': len(bundle['source_files']), 'scenarios': len(execution),
         'checks': sum(r['assertions'] for r in execution.values()),
         'ledger_fields': len(rows), 'ledger_dimensions': len(ledger),
         'physical_timing_verified': False, 'new_model_generation': False,
         'output_sha256': {name:sha(OUT/name) for name in
                           ('scenario_execution.json','repair_closure_ledger.json','admission_gate.json','remaining_repair_queue.json')}})
    print('Executed', len(execution), 'source-linked scenarios with',sum(r['assertions'] for r in execution.values()),'checks; production gate remains closed.')


if __name__ == '__main__':
    main()
