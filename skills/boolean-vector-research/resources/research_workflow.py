"""Construct -> core metrics -> optional S-box criteria -> hashed experiment folder.

python research_workflow.py --input project.json --out-dir new-experiment
No arbitrary expressions or code are evaluated; existing directories are never reused.
"""
import argparse
import hashlib
import json
import datetime
import platform
import sys
import time
from pathlib import Path
import research_core as core
import field_functions as field
import sbox_criteria as sbox


VERSION='0.2.2'


def compute(spec,emit=lambda stage,status:None):
    """Calculate reproducible mathematical outputs without creating any files."""
    emit('validation','started')
    if type(spec) is not dict or set(spec)-{'construction','advanced','sbox','include_sbox_tables','max_work','field_max_work'}:
        raise ValueError('unsupported project fields or non-object input')
    construction=spec.get('construction')
    if type(construction) is not dict or set(construction)!={'kind','params'} or type(construction['params']) is not dict:
        raise ValueError('construction needs exactly kind and params object')
    options={key:spec.get(key,default) for key,default in [('advanced',False),('sbox',True),('include_sbox_tables',False)]}
    for key,value in options.items():
        if type(value) is not bool:raise ValueError(f'{key} must be JSON boolean')
    work=core.integer(spec.get('max_work',25_000_000),'max_work',1,1_000_000_000)
    field_work=core.integer(spec.get('field_max_work',2_000_000),'field_max_work',1,100_000_000)
    emit('validation','completed')
    kind=construction['kind'];params=construction['params']
    emit('construction','started')
    if kind=='table':
        if set(params)!={'n','m','table'}:raise ValueError('table params require n,m,table only')
        function=dict(params)
    elif kind in ('trace','polynomial'):
        function=field.polynomial_table(params,trace=kind=='trace',max_work=field_work)
    elif kind in ('gold','mm','quadratic-bent'):
        allowed={'gold':{'n','k','polynomial'},'mm':{'n','pi','g'},'quadratic-bent':{'n'}}[kind]
        if set(params)-allowed or 'n' not in params:raise ValueError('unsupported constructor parameters')
        core.integer(params['n'],'n',1,8)
        function=core.construct_spec(kind,**params)
    else:raise ValueError('unsupported construction kind')
    emit('construction','completed')
    input_function={key:function[key] for key in ('n','m','table')}
    emit('core_analysis','started')
    analysis=core.analyze(input_function,advanced=options['advanced'],max_work=work)
    emit('core_analysis','completed')
    emit('sbox_analysis','started' if options['sbox'] else 'skipped')
    sbox_result=sbox.analyze(input_function,include_tables=options['include_sbox_tables'],max_work=work) if options['sbox'] else None
    if sbox_result is not None:emit('sbox_analysis','completed')
    data={'project.json':spec,'function.json':function,'analysis.json':analysis}
    if sbox_result is not None:data['sbox.json']=sbox_result
    return data,kind


def run(spec,out_dir):
    out_dir=Path(out_dir)
    if out_dir.exists():raise ValueError('experiment directory already exists; choose a new directory')
    events=[];start=time.perf_counter()
    def emit(stage,status):
        events.append(dict(sequence=len(events)+1,time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           elapsed_seconds=round(time.perf_counter()-start,6),stage=stage,status=status))
    data,kind=compute(spec,emit)
    analysis=data['analysis.json'];sbox_result=data.get('sbox.json')
    runtime=Path(__file__).resolve().parent
    data['environment.json']=dict(tool_version=VERSION,python=sys.version,implementation=platform.python_implementation(),
        platform=platform.platform(),created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        runtime_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(runtime.glob('*.py')) if not p.name.startswith('test_')},
        limitation='File fingerprints record provenance; they are not signatures or a security guarantee.')
    # Calculate all bounded stages before creating the directory; never leave a
    # mathematical-input failure looking like a successful partial experiment.
    out_dir.mkdir(parents=True,exist_ok=False)
    hashes={}
    for name,value in data.items():
        encoded=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        (out_dir/name).write_bytes(encoded);hashes[name]=hashlib.sha256(encoded).hexdigest()
    lines=[f'# Finite research experiment {VERSION}', '',
           f'Construction: {kind}; dimensions: {analysis["n"]} -> {analysis["m"]}.',
           f'Nonlinearity: {analysis["nonlinearity"]}; differential uniformity: {analysis["differential_uniformity"]}.',
           f'Permutation: {analysis["permutation"]}; balanced: {analysis["balanced"]}.',
           f'Generated-code rank: {analysis["generated_code"]["rank"]}; full-rank bridge: {analysis["generated_code"]["full_rank_bridge_applicable"]}.']
    if sbox_result is not None:
        lines.extend([f'BCT status: {sbox_result["bct"]["status"]}.',
                      f'DLCT count-bias maximum: {sbox_result["dlct"]["maximum_absolute_nontrivial_entry"]}.'])
    lines.extend(['','Exact finite input only. This is not a parameter-family proof, equivalence classification, novelty claim or security assessment.',
                  'Advanced fields may be not_computed outside their supported dimensions. Inspect their status.',
                  'A run is complete only when manifest.json exists and all listed hashes match.'])
    summary='\n'.join(lines)+'\n';(out_dir/'summary.md').write_bytes(summary.encode('utf-8'))
    hashes['summary.md']=hashlib.sha256(summary.encode('utf-8')).hexdigest()
    emit('artifact_files','written');emit('manifest','ready_to_finalize')
    log=(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events)).encode('utf-8')
    (out_dir/'execution.jsonl').write_bytes(log);hashes['execution.jsonl']=hashlib.sha256(log).hexdigest()
    manifest=dict(schema_version=2,status='complete',tool_version=VERSION,construction=kind,files=hashes,
                  limitations=['finite objects only','no automatic CCZ classification','no automatic literature novelty review'])
    (out_dir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    try:
        result=run(json.loads(a.input.read_text(encoding='utf-8-sig')),a.out_dir)
    except (ValueError,TypeError,OSError,KeyError) as e:p.exit(2,f'error: {e}\n')
    print(json.dumps(dict(status=result['status'],directory=str(a.out_dir),files=len(result['files']))))


if __name__=='__main__':main()
