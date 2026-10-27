"""Bounded, reproducible monomial search in GF(2^n), n<=6.

python search_monomials.py --input search.json --out results.json
Search is exhaustive only over the explicitly listed exponents, never all functions.
"""
import argparse
import json
import math
from pathlib import Path
from research_core import analyze, gf_pow, is_irreducible
from research_extensions import integer


def search(spec):
    n = integer(spec['n'], 2, 6)
    N = 1 << n
    polynomial = integer(spec['polynomial'], N+1, 2*N-1)
    if not is_irreducible(polynomial, n):
        raise ValueError('polynomial must be irreducible of degree n over F2')
    exponents = spec['exponents']
    if not isinstance(exponents, list) or not 1 <= len(exponents) <= 64:
        raise ValueError('provide 1..64 explicit exponents')
    if len(set(exponents)) != len(exponents):
        raise ValueError('duplicate exponents rejected')
    for d in exponents:
        integer(d, 1, N-2)
    filters = spec.get('filters', {})
    if not isinstance(filters, dict) or set(filters) - {'max_delta','min_nonlinearity','min_degree','require_permutation'}:
        raise ValueError('unknown filters')
    max_delta = integer(filters.get('max_delta', N), 2, N)
    min_nl = integer(filters.get('min_nonlinearity', 0), 0, N//2)
    min_deg = integer(filters.get('min_degree', 0), 0, n)
    perm = filters.get('require_permutation', False)
    if type(perm) is not bool:
        raise ValueError('require_permutation must be a JSON boolean')
    rows = []
    for d in exponents:
        table = [gf_pow(x, d, polynomial) for x in range(N)]
        result = analyze(dict(n=n,m=n,table=table))
        nl, delta = result['nonlinearity'], result['differential_uniformity']
        degrees = [c['degree'] for c in result['components']]
        degree = max(degrees)
        permutation = len(set(table)) == N
        accepted = delta <= max_delta and nl >= min_nl and degree >= min_deg and (not perm or permutation)
        rows.append(dict(exponent=d, table=table, nonlinearity=nl,
                         differential_uniformity=delta, degree=degree,
                         permutation=permutation, permutation_exponent_test=math.gcd(d,N-1)==1,
                         accepted=accepted))
    return dict(status='exact_over_explicit_exponents', input=spec, candidates=rows,
                accepted_exponents=[r['exponent'] for r in rows if r['accepted']],
                novelty='not_evaluated', equivalence='not_deduplicated',
                limitation='No global optimality, novelty, or inequivalence claim. All nonzero components and directions checked for each finite table.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.out.resolve():
            raise ValueError('output must not overwrite input')
        spec = json.loads(args.input.read_text(encoding='utf-8-sig'))
        if not isinstance(spec, dict):
            raise ValueError('input must be JSON object')
        result = search(spec)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(dict(status='ok',tested=len(result['candidates']),accepted=result['accepted_exponents'])))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2,f'Input/search error: {exc}\n')


if __name__=='__main__': main()
