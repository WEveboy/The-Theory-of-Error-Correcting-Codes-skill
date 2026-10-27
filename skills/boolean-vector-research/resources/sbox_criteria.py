"""Exact BCT, count-bias DLCT, coordinate SAC and all-component PC (n<=8)."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from research_core import integer, ResearchError, fwht, parity


def analyze(spec, include_tables=False, max_work=25_000_000):
    integer(max_work,'max_work',1,1_000_000_000)
    if type(include_tables) is not bool or type(spec) is not dict:
        raise ResearchError('JSON object and boolean include_tables required')
    n=integer(spec.get('n'),'n',1,8); m=integer(spec.get('m'),'m',1,n)
    N=1 << n; M=1 << m; table=spec.get('table')
    if type(table) is not list or len(table)!=N: raise ResearchError('table length must equal 2**n')
    for y in table:integer(y,'table value',0,M-1)
    permutation=n==m and len(set(table))==N
    work=(N-1)*N+(N-1)*m*M+((N-1)**2*N if permutation else 0)
    if work>max_work:raise ResearchError(f'estimated work {work} exceeds max_work={max_work}')
    dlct=[]; hist=Counter(); worst=None; amplitude=-1; counts_by_unit=[]; pc_failure=None
    for u in range(1,N):
        counts=[0]*M
        for x in range(N):counts[table[x]^table[x^u]]+=1
        ac=fwht(counts)
        assert all(v%2==0 for v in ac)
        row=[v//2 for v in ac]
        hist.update(row[1:])
        for b in range(1,M):
            if abs(row[b])>amplitude:amplitude=abs(row[b]);worst=dict(direction=u,output_mask=b,value=row[b])
            if row[b] and (pc_failure is None or u.bit_count()<pc_failure['input_weight']):
                pc_failure=dict(direction=u,input_weight=u.bit_count(),output_mask=b,value=row[b])
        if u.bit_count()==1:
            counts_by_unit.append(dict(direction=u,ones=[(N-ac[1 << j])//2 for j in range(m)]))
        if include_tables:dlct.append(dict(direction=u,count_bias=row))
    sac=all(v==N//2 for r in counts_by_unit for v in r['ones'])
    sac_witness=next((dict(direction=r['direction'],coordinate=j,ones=v,expected=N//2)
                      for r in counts_by_unit for j,v in enumerate(r['ones']) if v!=N//2),None)
    pc_order=n if pc_failure is None else pc_failure['input_weight']-1
    bct=dict(status='not_applicable',reason='classical inverse-based BCT requires a square permutation')
    if permutation:
        inv=[0]*N
        for x,y in enumerate(table):inv[y]=x
        rows=[]; bh=Counter(); beta=-1; witness=None
        for a in range(1,N):
            row=[N]
            for b in range(1,N):
                inputs=[x for x in range(N) if inv[table[x]^b]^inv[table[x^a]^b]==a]
                value=len(inputs);row.append(value);bh[value]+=1
                if value>beta:beta=value;witness=dict(input_difference=a,output_difference=b,count=value,input_witnesses=inputs)
            if include_tables:rows.append(dict(input_difference=a,counts=row))
        bct=dict(status='exact',boomerang_uniformity=beta,worst_entry=witness,
                 histogram_nonzero_rows_and_columns=dict(sorted(bh.items())),
                 definition='BCT(a,b)=#{x: inv(F(x)^b)^inv(F(x^a)^b)==a}; a=input difference; b=output difference')
        if include_tables:bct['nonzero_row_table']=rows
    result=dict(schema_version=1,status='exact_finite_sbox_criteria',input=spec,n=n,m=m,
        budget=dict(estimated_work_units=work,max_work=max_work),
        dlct=dict(status='exact',normalization='count_bias: #equal-N/2 = unnormalized autocorrelation/2',
                  maximum_absolute_nontrivial_entry=amplitude,worst_entry=worst,
                  histogram_nonzero_directions_and_masks=dict(sorted(hist.items()))),
        coordinate_sac=dict(satisfied=sac,unit_direction_output_bit_ones=counts_by_unit,failure_witness=sac_witness),
        all_component_pc=dict(order=pc_order,failure_witness=pc_failure,
            definition='all b!=0 components have balanced derivatives for every u with 1<=wt(u)<=order; stronger than coordinate SAC'),
        bct=bct,limitation='Finite properties only; BCT/DLCT are not used as CCZ invariants or as a system-security guarantee.')
    if include_tables:result['dlct']['nonzero_direction_rows']=dlct
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['analyze'])
    p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--include-tables',action='store_true');p.add_argument('--max-work',type=int,default=25_000_000)
    a=p.parse_args()
    try:
        if a.input.resolve()==a.out.resolve():raise ResearchError('output must not overwrite input')
        result=analyze(json.loads(a.input.read_text(encoding='utf-8-sig')),a.include_tables,a.max_work)
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    except (ResearchError,OSError,json.JSONDecodeError) as e:p.exit(2,f'error: {e}\n')
    print(json.dumps(dict(status=result['status'],output=str(a.out))))


if __name__=='__main__':main()
