import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    skill=ROOT/'skills/boolean-vector-research';edition=json.loads((skill/'EDITION.json').read_text(encoding='utf-8'))
    for name,h in edition['files'].items():assert hashlib.sha256((skill/name).read_bytes()).hexdigest()==h,name
    checked=0
    for p in ROOT.rglob('*.md'):
        if 'build' in p.parts or 'dist' in p.parts:continue
        for link in re.findall(r'\]\(([^\n)]+)\)',p.read_text(encoding='utf-8')):
            link=link.split('#')[0].strip('<>')
            if not link or re.match(r'[a-zA-Z]+:',link):continue
            assert (p.parent/link).exists(),str(p)+': '+link
            checked+=1
    for name in ['Codex-First-Edition.pdf','DeepSeek-First-Edition.pdf']:
        assert (ROOT/'docs/tutorial'/name).read_bytes().startswith(b'%PDF-'),name
    assert len(list((skill/'references/capabilities').glob('*.md')))==16
    print(json.dumps(dict(status='PASS',frozen_files=len(edition['files']),relative_links=checked,capabilities=16)))
if __name__=='__main__':main()
