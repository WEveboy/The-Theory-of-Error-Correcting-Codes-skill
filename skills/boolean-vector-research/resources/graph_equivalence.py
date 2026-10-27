"""Given CCZ graph-affine certificates and necessary-invariant prefilters only."""
import argparse
from collections import Counter
import json
from pathlib import Path
from research_core import fwht, parity, integer, ResearchError, gf2_basis


def validate(spec, table_key='table'):
    if type(spec) is not dict:raise ResearchError('JSON object required')
    n=integer(spec.get('n'),'n',1,8);m=integer(spec.get('m'),'m',1,n)
    table=spec.get(table_key);N=1 << n;M=1 << m
    if type(table) is not list or len(table)!=N:raise ResearchError(f'{table_key} length must be 2**n')
    for y in table:integer(y,table_key,0,M-1)
    return n,m,table


def certificate(spec,max_work=25_000_000):
    n,m,table=validate(spec);d=n+m;N=1 << n;mask=N-1
    if set(spec)-{'n','m','table','graph_rows','graph_shift','target'}:
        raise ResearchError('unsupported certificate fields; use graph_shift for translation')
    integer(max_work,'max_work',1,1_000_000_000)
    if N*d*d+d*d>max_work:raise ResearchError('certificate work exceeds max_work')
    rows=spec.get('graph_rows')
    if type(rows) is not list or len(rows)!=d:raise ResearchError('graph_rows needs n+m row masks')
    for r in rows:integer(r,'graph row',0,(1 << d)-1)
    if len(gf2_basis(rows))!=d:raise ResearchError('graph matrix must be invertible')
    shift=integer(spec.get('graph_shift',0),'graph_shift',0,(1 << d)-1)
    target=spec.get('target')
    if target is not None:validate(dict(n=n,m=m,table=target))
    transformed=[None]*N;original=[None]*N
    for x,y in enumerate(table):
        z=x|(y << n);w=sum(parity(r&z) << i for i,r in enumerate(rows))^shift
        u=w&mask;v=w >> n
        if transformed[u] is not None:
            return dict(status='not_function_graph',input=spec,
                witness=dict(projected_input=u,original_inputs=[original[u],x],outputs=[transformed[u],v]),
                reason='low-n-bit input projection is not bijective; cannot represent transformed graph as a total n->m function')
        transformed[u]=v;original[u]=x
    mismatch=next((dict(input=x,transformed=v,target=target[x]) for x,v in enumerate(transformed) if target is not None and v!=target[x]),None)
    return dict(status='verified_graph_affine_certificate',input=spec,n=n,m=m,table=transformed,
        matches_target=None if target is None else mismatch is None,first_mismatch=mismatch,
        bit_convention='z=x|(F(x)<<n); row i computes output bit i; low n bits are new inputs',
        limitation='Verifies only this explicit invertible graph-affine map; does not search for CCZ equivalence.')


def invariants(n,m,table,max_work):
    N=1 << n;M=1 << m
    work=M*N*n+N*(N-1)
    if work>max_work:raise ResearchError(f'prefilter work {work} exceeds max_work={max_work}')
    spectrum=Counter()
    for b in range(M):
        values=fwht([1-2*parity(b&y) for y in table])
        spectrum.update(abs(v) for a,v in enumerate(values) if a or b)
    differential=Counter()
    for u in range(1,N):
        counts=[0]*M
        for x in range(N):counts[table[x]^table[x^u]]+=1
        differential.update(counts)
    return dict(absolute_graph_walsh_histogram=dict(sorted(spectrum.items())),
                ddt_nonzero_direction_histogram=dict(sorted(differential.items())))


def prefilter(spec,max_work=25_000_000):
    integer(max_work,'max_work',1,1_000_000_000)
    n,m,left=validate(spec,'left');_,_,right=validate(spec,'right')
    if set(spec)-{'n','m','left','right'}:raise ResearchError('unsupported prefilter fields')
    # The budget bounds both complete computations, not only one side.
    if 2*((1 << m)*(1 << n)*n+(1 << n)*((1 << n)-1))>max_work:
        raise ResearchError('combined prefilter work exceeds max_work')
    L=invariants(n,m,left,max_work);R=invariants(n,m,right,max_work)
    differs=[key for key in L if L[key]!=R[key]]
    return dict(status='proven_not_ccz_equivalent' if differs else 'inconclusive',n=n,m=m,
                differing_invariants=differs,left=L,right=R,
                definition='All nonzero graph characters (a,b)!=(0,0), including b=0; DDT all u!=0 and all output differences.',
                limitation='Matching invariants never prove equivalence; no CCZ search/canonical form. Degree, BCT and DLCT are not asserted as CCZ invariants.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['certificate','prefilter'])
    p.add_argument('--input',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--max-work',type=int,default=25_000_000);a=p.parse_args()
    try:
        if a.input.resolve()==a.out.resolve():raise ResearchError('output must not overwrite input')
        spec=json.loads(a.input.read_text(encoding='utf-8-sig'))
        result=certificate(spec,a.max_work) if a.operation=='certificate' else prefilter(spec,a.max_work)
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    except (ResearchError,OSError,json.JSONDecodeError) as e:p.exit(2,f'error: {e}\n')
    print(json.dumps(dict(status=result['status'],output=str(a.out))))


if __name__=='__main__':main()
