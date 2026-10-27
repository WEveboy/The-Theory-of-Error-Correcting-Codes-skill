"""Prepare both platforms from one frozen skill, then build versioned archives."""
import argparse,gzip,hashlib,json,shutil,tarfile,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='1.0.0'

def copied(source,target):shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
def files(root):return [p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source_files():
    allowed={'skills','source','platforms','scripts','tests','docs','examples','.github'}
    roots={'README.md','AGENTS.md','CHANGELOG.md','release-info.json','.gitignore','.gitattributes'}
    return [p for p in files(ROOT) if ((p.relative_to(ROOT).parts[0] in allowed) or p.relative_to(ROOT).as_posix() in roots) and p.suffix not in ('.aux','.log','.toc','.out','.pyc')]
def archive(path,entries):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,27,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');a=parser.parse_args()
    skill=ROOT/'skills/boolean-vector-research';build=ROOT/'build';dsh=build/'deepseek-package';codex=build/'codex-package'
    copied(skill,dsh/'skills/boolean-vector-research');copied(skill,codex/'boolean-vector-research')
    for p in (ROOT/'platforms/deepseek').iterdir():
        if p.is_file():shutil.copyfile(p,dsh/p.name)
    (dsh/'README.md').write_text('第一版V1 / 1.0.0。DeepSeek Harness插件。完整教程见GitHub仓库docs/tutorial；运行资源见skills/boolean-vector-research/resources/usage.md。\n',encoding='utf-8',newline='\n')
    shutil.copyfile(ROOT/'scripts/install_codex.py',codex/'install_codex.py')
    shutil.copyfile(ROOT/'README.md',codex/'README.md')
    if a.prepare_only:print(json.dumps(dict(status='prepared',platforms=['codex','deepseek'],version=VERSION)));return
    for guide in ['Codex-First-Edition.pdf','DeepSeek-First-Edition.pdf']:
        if not (ROOT/'docs/tutorial'/guide).is_file():raise ValueError('compile tutorials before packaging: '+guide)
    copied(ROOT/'docs/tutorial',codex/'docs/tutorial')
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    tgz=out/f'dsh-boolean-vector-research-{VERSION}.tgz'
    with tgz.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w') as tar:
                for p in files(dsh):
                    info=tar.gettarinfo(str(p),'package/'+p.relative_to(dsh).as_posix());info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o644
                    with p.open('rb') as f:tar.addfile(info,f)
    with tarfile.open(tgz) as t:
        assert t.getmember('package/index.mjs').isfile();assert t.getmember('package/skills/boolean-vector-research/SKILL.md').isfile()
    codexzip=out/f'boolean-vector-research-Codex-{VERSION}.zip';archive(codexzip,{p.relative_to(codex).as_posix():p for p in files(codex) if p.suffix not in ('.aux','.log','.toc','.out')})
    dshzip=out/f'boolean-vector-research-DeepSeek-{VERSION}.zip'
    entries={tgz.name:tgz,'README.md':ROOT/'README.md'}
    entries.update({'docs/tutorial/'+p.relative_to(ROOT/'docs/tutorial').as_posix():p for p in files(ROOT/'docs/tutorial') if p.suffix in ('.tex','.md','.pdf')})
    archive(dshzip,entries)
    sourcezip=out/f'boolean-vector-research-source-{VERSION}.zip';archive(sourcezip,{'boolean-vector-research-skills/'+p.relative_to(ROOT).as_posix():p for p in source_files()})
    assets=[codexzip,dshzip,tgz,sourcezip]
    for guide in ['Codex-First-Edition.pdf','DeepSeek-First-Edition.pdf']:
        p=out/guide;shutil.copyfile(ROOT/'docs/tutorial'/guide,p);assets.append(p)
    (out/'SHA256SUMS.txt').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in assets),encoding='utf-8',newline='\n')
    metadata=dict(public_version=VERSION,edition='第一版',baseline='0.2.2',assets={p.name:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in assets},source_files=len(source_files()))
    (build/'package-validation.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False))

if __name__=='__main__':main()
