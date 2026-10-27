"""Read-only hash audit and optional bounded recomputation of research experiments.

python experiment_audit.py --directory experiment-001 [--recompute] [--out audit.json]
Hash consistency is not authenticity: a manifest can be rewritten with its files.
"""
import argparse
import hashlib
import json
import re
import datetime
import math
from pathlib import Path
import research_workflow as workflow

MAX_FILE_BYTES=64*1024*1024
MAX_TOTAL_BYTES=128*1024*1024


class AuditError(ValueError):pass


def read_bounded(path,limit=MAX_FILE_BYTES):
    if path.is_symlink() or not path.is_file():raise AuditError('missing, symlink or non-file: '+path.name)
    if path.stat().st_size>limit:raise AuditError('file exceeds audit size limit: '+path.name)
    with path.open('rb') as f:data=f.read(limit+1)
    if len(data)>limit:raise AuditError('file changed beyond audit size limit: '+path.name)
    return data


def decode(data,name):
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError('duplicate object key')
            value[key]=item
        return value
    def finite(value):raise ValueError('non-finite JSON number')
    def finite_float(value):
        result=float(value)
        if not math.isfinite(result):raise ValueError('non-finite JSON number')
        return result
    try:return json.loads(data.decode('utf-8-sig'),object_pairs_hook=unique,parse_constant=finite,parse_float=finite_float)
    except (ValueError,UnicodeError,RecursionError) as e:raise AuditError('invalid JSON: '+name) from e


def first_difference(expected,actual,pointer=''):
    """Find one typed JSON difference, using RFC6901-style escaped tokens."""
    def preview(value):
        text=json.dumps(value,ensure_ascii=False,allow_nan=False)
        return text if len(text)<=240 else text[:237]+'...'
    def witness(reason):return dict(pointer=pointer,reason=reason,expected=preview(expected),actual=preview(actual))
    if type(expected) is not type(actual):return witness('type_mismatch')
    if isinstance(expected,dict):
        for key in sorted(set(expected)|set(actual)):
            token=str(key).replace('~','~0').replace('/','~1');path=pointer+'/'+token
            if key not in expected:return dict(pointer=path,reason='unexpected_key')
            if key not in actual:return dict(pointer=path,reason='missing_key')
            difference=first_difference(expected[key],actual[key],path)
            if difference:return difference
    elif isinstance(expected,list):
        if len(expected)!=len(actual):return dict(pointer=pointer,reason='length_mismatch',expected_length=len(expected),actual_length=len(actual))
        for i,(left,right) in enumerate(zip(expected,actual)):
            difference=first_difference(left,right,pointer+'/'+str(i))
            if difference:return difference
    elif expected!=actual:return witness('value_mismatch')
    return None


def utc_timestamp(value,name):
    if type(value) is not str or len(value)>64:raise AuditError('invalid UTC timestamp: '+name)
    try:stamp=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as e:raise AuditError('invalid UTC timestamp: '+name) from e
    if stamp.tzinfo is None or stamp.utcoffset()!=datetime.timedelta(0):raise AuditError('UTC offset required: '+name)


def check_provenance(buffers,manifest,project):
    """Check self-reported provenance structure, not its authenticity."""
    failures=[];recorded=None
    if 'environment.json' in buffers:
        env=decode(buffers['environment.json'],'environment.json')
        if type(env) is not dict:raise AuditError('environment must be a JSON object')
        if env.get('tool_version')!=manifest['tool_version']:raise AuditError('environment/manifest version mismatch')
        for key in ('python','implementation','platform'):
            if type(env.get(key)) is not str or not 1<=len(env[key])<=4096:raise AuditError('invalid environment.'+key)
        utc_timestamp(env.get('created_utc'),'environment.created_utc')
        recorded=env.get('runtime_sha256')
        if type(recorded) is not dict or not 1<=len(recorded)<=32:raise AuditError('runtime provenance needs 1..32 hashes')
        for name,digest in recorded.items():
            if not re.fullmatch(r'[A-Za-z0-9_]+\.py',name) or type(digest) is not str or not re.fullmatch('[0-9a-f]{64}',digest):
                raise AuditError('invalid runtime provenance hash/name')
    if 'execution.jsonl' in buffers:
        try:lines=buffers['execution.jsonl'].decode('utf-8-sig').splitlines()
        except UnicodeError as e:raise AuditError('invalid UTF8 execution log') from e
        if not 1<=len(lines)<=64:raise AuditError('execution log needs 1..64 events')
        rows=[decode(line.encode('utf-8'),'execution.jsonl') for line in lines]
        expected=[('validation','started'),('validation','completed'),('construction','started'),('construction','completed'),('core_analysis','started'),('core_analysis','completed')]
        expected+=([('sbox_analysis','started'),('sbox_analysis','completed')] if project.get('sbox',True) else [('sbox_analysis','skipped')])
        expected += [('artifact_files','written'),('manifest','ready_to_finalize')]
        elapsed=-1
        for i,row in enumerate(rows):
            if type(row) is not dict:raise AuditError('execution events must be JSON objects')
            utc_timestamp(row.get('time_utc'),'execution.time_utc')
            value=row.get('elapsed_seconds')
            if type(value) not in (int,float) or value<0 or value>1e12 or not math.isfinite(value):raise AuditError('invalid event elapsed time')
            if type(row.get('sequence')) is not int or row['sequence']!=i+1:
                failures.append(dict(file='execution.jsonl',issue='invalid_sequence',witness=dict(pointer='/'+str(i)+'/sequence',expected=i+1,actual=row.get('sequence'))))
            if value<elapsed:failures.append(dict(file='execution.jsonl',issue='elapsed_time_decreased',witness=dict(pointer='/'+str(i)+'/elapsed_seconds')))
            elapsed=value
        observed=[[row.get('stage'),row.get('status')] for row in rows]
        difference=first_difference([list(pair) for pair in expected],observed)
        if difference:failures.append(dict(file='execution.jsonl',issue='stage_protocol_mismatch',witness=difference))
    return failures,recorded


def verify(directory,recompute=False,max_work=25_000_000):
    if type(recompute) is not bool:raise AuditError('recompute must be boolean')
    if type(max_work) is not int or not 1<=max_work<=1_000_000_000:raise AuditError('invalid max_work')
    root=Path(directory).resolve()
    manifest=decode(read_bounded(root/'manifest.json',1024*1024),'manifest.json')
    if type(manifest) is not dict or manifest.get('status')!='complete':raise AuditError('manifest is not complete')
    if manifest.get('tool_version') not in ('0.2.0','0.2.1','0.2.2'):raise AuditError('unsupported experiment version')
    hashes=manifest.get('files')
    if type(hashes) is not dict or not 1<=len(hashes)<=32:raise AuditError('manifest.files needs 1..32 entries')
    required={'project.json','function.json','analysis.json','summary.md'}
    if manifest['tool_version'] in ('0.2.1','0.2.2'):required|={'environment.json','execution.jsonl'}
    if not required<=set(hashes):raise AuditError('required experiment files missing from manifest')
    buffers={};failures=[];total=0
    for name,expected in hashes.items():
        if type(name) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',name) or name=='manifest.json':
            raise AuditError('manifest entries must be safe basenames, not paths')
        if type(expected) is not str or not re.fullmatch('[0-9a-f]{64}',expected):raise AuditError('invalid SHA256 value')
        path=root/name
        if path.resolve().parent!=root:raise AuditError('file escapes experiment directory')
        data=read_bounded(path);total+=len(data)
        if total>MAX_TOTAL_BYTES:raise AuditError('total audit size exceeds limit')
        buffers[name]=data
        actual=hashlib.sha256(data).hexdigest()
        if actual!=expected:failures.append(dict(file=name,issue='sha256_mismatch',expected=expected,actual=actual))
    result=dict(status='hash_mismatch' if failures else 'hash_consistent',files_checked=len(hashes),bytes_checked=total,
        experiment_version=manifest['tool_version'],failures=failures,recomputation='not_requested',
        authenticity='not_established: hashes and manifest are unsigned',
        scope='Read-only finite experiment audit, not a theorem proof, signature check or equivalence classifier.')
    if failures:
        if recompute:result['recomputation']='skipped_due_to_hash_mismatch'
        return result
    # Cross-file consistency matters even when someone updates the manifest hashes.
    project=decode(buffers['project.json'],'project.json');function=decode(buffers['function.json'],'function.json');analysis=decode(buffers['analysis.json'],'analysis.json')
    if type(project) is not dict or type(function) is not dict or type(analysis) is not dict:raise AuditError('experiment JSON objects required')
    table={key:function.get(key) for key in ('n','m','table')}
    if first_difference(table,analysis.get('input')) or analysis.get('status')!='exact_finite_analysis':
        failures.append(dict(file='analysis.json',issue='function_analysis_input_mismatch'))
    if type(project.get('sbox',True)) is not bool:raise AuditError('project.sbox must be boolean')
    has_sbox='sbox.json' in buffers
    if has_sbox!=project.get('sbox',True):failures.append(dict(file='sbox.json',issue='project_sbox_presence_mismatch'))
    if has_sbox:
        sbox=decode(buffers['sbox.json'],'sbox.json')
        if type(sbox) is not dict or first_difference(table,sbox.get('input')):failures.append(dict(file='sbox.json',issue='function_sbox_input_mismatch'))
    provenance_failures,recorded=check_provenance(buffers,manifest,project)
    failures.extend(provenance_failures)
    if recompute and not failures:
        # Do not let archived projects silently raise the caller's replay budget.
        for key,default in [('max_work',25_000_000),('field_max_work',2_000_000)]:
            v=project.get(key,default)
            if type(v) is not int or not 1<=v<=max_work:raise AuditError('archived '+key+' exceeds recomputation budget; explicitly raise --max-work')
        try:regenerated,_=workflow.compute(project)
        except (ValueError,TypeError,KeyError) as e:raise AuditError('recomputation failed: '+str(e)) from e
        for name in ('function.json','analysis.json','sbox.json'):
            if name in regenerated:
                stored=decode(buffers[name],name)
                # JSON object keys are strings on disk (histograms use integer
                # keys in Python). Compare the serialized data model, not the
                # pre-serialization Python dictionary key types.
                normalized=json.loads(json.dumps(regenerated[name],ensure_ascii=False))
                difference=first_difference(normalized,stored)
                if difference:failures.append(dict(file=name,issue='recomputed_value_mismatch',witness=difference))
        result['recomputation']='mismatch' if failures else 'matched'
    if recorded is not None:
        current={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(workflow.__file__).resolve().parent.glob('*.py') if not p.name.startswith('test_')}
        result['runtime_fingerprints_match']=recorded==current
        result['runtime_note']='A changed runtime is reported separately; mathematical replay is the decisive recomputation comparison.'
    result['failures']=failures
    if recompute and failures and result['recomputation']=='not_requested':result['recomputation']='skipped_due_to_content_mismatch'
    result['status']='content_mismatch' if failures else ('recomputed_match' if recompute else 'hash_consistent')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path)
    p.add_argument('--recompute',action='store_true');p.add_argument('--max-work',type=int,default=25_000_000);p.add_argument('--out',type=Path);a=p.parse_args()
    try:
        if a.out and (a.out.exists() or a.out.resolve().is_relative_to(a.directory.resolve())):
            raise AuditError('audit output must be a new file outside the experiment directory')
        result=verify(a.directory,a.recompute,a.max_work)
        encoded=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if a.out:
            a.out.parent.mkdir(parents=True,exist_ok=True)
            with a.out.open('xb') as f:f.write(encoded.encode('utf-8'))
        print(encoded,end='')
    except (AuditError,OSError) as e:p.exit(2,'error: '+str(e)+'\n')
    if result['failures']:raise SystemExit(1)

if __name__=='__main__':main()
