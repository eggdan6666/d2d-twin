"""Before commit, verify this archive is the entire staged change and exact bytes."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf-8').strip()


def main():
    manifest=json.loads((OUT/'artifact_manifest.json').read_text(encoding='utf-8'))
    prefix=OUT.relative_to(ROOT).as_posix()+'/'
    expected={prefix+name for name in manifest['files']}
    expected.add(prefix+'artifact_manifest.json')
    expected.update(manifest['helper_sha256'])
    staged=set(git('-c','core.quotepath=false','diff','--cached','--name-only').splitlines())
    assert staged==expected|{'.gitattributes'},'Staged scope differs from this archive'
    for rel in sorted(expected):
        blob=(ROOT/rel).read_bytes()
        oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
        assert git('rev-parse',':'+rel)==oid,'Staged bytes differ: '+rel
    print('Staged archive verified:',len(expected),'exact byte files plus scoped .gitattributes')


if __name__=='__main__':main()
