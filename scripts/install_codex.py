"""Install the first edition, refusing accidental overwrite and preserving backups."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path

NAME='boolean-vector-research'
BASE=Path(__file__).resolve().parent

def source_directory():
    for p in [BASE/NAME,BASE.parent/'skills'/NAME]:
        if (p/'EDITION.json').is_file():return p
    raise ValueError('cannot locate the complete first-edition skill folder')

def install(root=None,replace=False):
    source=source_directory()
    edition=json.loads((source/'EDITION.json').read_text(encoding='utf-8'))
    for name,digest in edition['files'].items():
        p=source/name
        if p.resolve().is_relative_to(source.resolve()) is False or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError('source integrity check failed: '+name)
    if root is None:
        legacy=Path.home()/'.codex/skills';root=legacy if (legacy/NAME).exists() else Path.home()/'.agents/skills'
    root=Path(root).expanduser().resolve();target=root/NAME
    if target.is_symlink():raise ValueError('existing target is a symlink; choose an explicit separate destination')
    if target.exists() and not replace:raise ValueError('skill already exists; use --replace only for an intentional backed-up upgrade')
    backup=None
    if target.exists():
        backup=root/(NAME+'.backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        if backup.resolve().parent!=root or target.resolve().parent!=root:raise ValueError('backup/target containment check failed')
        shutil.copytree(target,backup)
    target.mkdir(parents=True,exist_ok=True)
    copied={}
    for p in source.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            name=p.relative_to(source);dest=target/name
            if not dest.resolve().is_relative_to(target.resolve()):raise ValueError('target child escapes skill directory')
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            copied[name.as_posix()]=hashlib.sha256(dest.read_bytes()).hexdigest()
    assert all(copied[name]==value for name,value in edition['files'].items())
    return dict(status='installed_and_verified',edition='第一版',public_version='1.0.0',target=str(target),backup=str(backup) if backup else None,files=len(copied),discovery='reload_or_start_new_task_if_needed')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path);p.add_argument('--replace',action='store_true');a=p.parse_args()
    try:result=install(a.destination,a.replace)
    except (ValueError,OSError) as e:p.exit(2,'error: '+str(e)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
