"""Exercise the actual distributed archives in an isolated new directory."""
import argparse,json,subprocess,sys,tarfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'build/archive-smoke');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);cases=[]
    def run(name,command,expected=0):
        r=subprocess.run([sys.executable,*map(str,command)],capture_output=True,text=True,encoding='utf-8')
        (a.out/(name+'.stdout.log')).write_text(r.stdout,encoding='utf-8');(a.out/(name+'.stderr.log')).write_text(r.stderr,encoding='utf-8')
        assert r.returncode==expected,(name,r.stderr);cases.append(dict(case=name,status='PASS',exit_code=r.returncode));return r
    codex=a.out/'codex';codex.mkdir()
    with zipfile.ZipFile(ROOT/'dist/boolean-vector-research-Codex-1.0.0.zip') as z:
        for name in z.namelist():assert (codex/name).resolve().is_relative_to(codex.resolve())
        z.extractall(codex)
    installed=a.out/'installed';r=run('codex-install',[codex/'install_codex.py','--destination',installed]);codexskill=Path(json.loads(r.stdout)['target'])
    dsh=a.out/'dsh';dsh.mkdir()
    with tarfile.open(ROOT/'dist/dsh-boolean-vector-research-1.0.0.tgz') as t:
        for member in t.getmembers():
            dest=dsh/member.name;assert member.isfile() and dest.resolve().is_relative_to(dsh.resolve());dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.extractfile(member).read())
    for name,skill in [('codex',codexskill),('deepseek',dsh/'package/skills/boolean-vector-research')]:
        out=a.out/name/'results';out.mkdir(parents=True);res=skill/'resources'
        project=ROOT/'examples/project.json';experiment=out/'experiment'
        run(name+'-workflow',[res/'research_workflow.py','--input',project,'--out-dir',experiment])
        r=run(name+'-audit',[res/'experiment_audit.py','--directory',experiment,'--recompute']);assert json.loads(r.stdout)['status']=='recomputed_match'
        run(name+'-bent',[res/'research_core.py','demo','--case','scalar-bent','--out',out/'bent.json']);assert json.loads((out/'bent.json').read_text())['nonlinearity']==6
        run(name+'-trace',[res/'field_functions.py','trace','--input',ROOT/'examples/field.json','--out',out/'trace.json'])
        run(name+'-trace-analysis',[res/'research_core.py','analyze','--input',out/'trace.json','--out',out/'trace-analysis.json'])
        certificate=out/'certificate.json';certificate.write_text(json.dumps(dict(n=2,m=2,table=list(range(4)),graph_rows=[4,8,1,2],graph_shift=0,target=list(range(4)))))
        run(name+'-graph',[res/'graph_equivalence.py','certificate','--input',certificate,'--out',out/'graph.json']);assert json.loads((out/'graph.json').read_text())['matches_target']
    result=dict(status='PASS',commands=len(cases),cases=cases)
    (a.out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(dict(status='PASS',commands=len(cases))))

if __name__=='__main__':main()
