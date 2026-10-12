"""Preserve the initial v2 run and all its inputs before the reviewed correction."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/protocol_v2_20261012'
ARCHIVE = OUT / 'audit_round_1'


def main():
    assert not ARCHIVE.exists(), 'Audit round already archived; do not overwrite'
    manifest = json.loads((OUT / 'protocol_manifest.json').read_text(encoding='utf-8'))
    assert manifest['version'] == '2.0-candidate-20261012'
    for rel, expected in manifest['files'].items():
        source = OUT / rel
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, rel
        target = ARCHIVE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for source in OUT.iterdir():
        if source.is_file() and source.suffix in ('.json', '.md', '.yaml', '.csv', '.log', '.zip'):
            shutil.copyfile(source, ARCHIVE / source.name)
    # The actual harness, helper, inputs and traces of the initial run are above.
    (ARCHIVE / 'AUDIT_STATUS.md').write_text(
        '# Superseded initial protocol run\n\n'
        'Retained evidence, not the accepted candidate scorer. An inherited MPU6050 '
        'DEVICE_RESET tier=UNVERIFIED caused this source-reviewed trigger to be skipped. '
        'The apparent Qwen14B gain was caused by that exclusion, not a model improvement. '
        'Protocol2.0-candidate-20261012.1 restores the source-backed atomic reset comparison. '
        'All original v1 and generated code records are preserved.\n', encoding='utf-8')
    payloads = {p.relative_to(ARCHIVE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in ARCHIVE.rglob('*') if p.is_file()}
    (ARCHIVE / 'archive_manifest.json').write_text(json.dumps(payloads, indent=2), encoding='utf-8')
    assert all(hashlib.sha256((ARCHIVE / rel).read_bytes()).hexdigest() == value for rel, value in payloads.items())
    # Remove just the superseded generated output after exact-byte archival;
    # this allows prepare to construct the distinctly numbered corrected inputs.
    assert (ARCHIVE / 'model_results.json').read_bytes() == (OUT / 'model_results.json').read_bytes()
    (OUT / 'model_results.json').unlink()
    print('AUDIT ROUND1 ARCHIVED; old inputs and outputs preserved', flush=True)


if __name__ == '__main__':
    main()
