"""Exact GF(2^n) polynomial/absolute-trace tables and trace-dual bases.

Python 3.10+, standard library. Field integers use polynomial-basis coordinates:
bit i is the coefficient of X^i. Arbitrary bases are accepted only by dual-basis.
No eval or symbolic parser is used. The original input is retained in results.
"""
import argparse
import json
import sys
from pathlib import Path

from research_core import gf_mul, gf_pow, is_irreducible

MAX_N = 8
MAX_EXPONENT = 1 << 20
MAX_TERMS = 64


class FieldError(ValueError):
    pass


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise FieldError(f'{name} must be an integer in [{low}, {high}]; booleans rejected')
    return value


def validate_field(spec, allowed):
    if type(spec) is not dict:
        raise FieldError('input must be a JSON object')
    if set(spec) - allowed:
        raise FieldError('unknown input fields: ' + ', '.join(sorted(set(spec) - allowed)))
    n = integer(spec.get('n'), 'n', 1, MAX_N)
    N = 1 << n
    polynomial = integer(spec.get('polynomial'), 'polynomial', N, 2*N-1)
    if not is_irreducible(polynomial, n):
        raise FieldError('polynomial must be irreducible of degree n over F2')
    return n, N, polynomial


def absolute_trace(x, n, polynomial):
    """Tr(x)=x+x^2+...+x^(2^(n-1)) as a field element, necessarily 0 or 1."""
    value, power = 0, x
    for _ in range(n):
        value ^= power
        power = gf_mul(power, power, polynomial)
    if value not in (0, 1):
        raise AssertionError('trace did not land in F2')
    return value


def basis_rank(values):
    pivots = {}
    for row in values:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def budget(estimated, max_work):
    integer(max_work, 'max_work', 1, 100_000_000)
    if estimated > max_work:
        raise FieldError(f'estimated work {estimated} exceeds max_work={max_work}')
    return dict(estimated_work_units=estimated, max_work=max_work,
                convention='conservative algebraic-operation estimate, not a timing promise')


def field_metadata(n, polynomial):
    return dict(n=n, irreducible_polynomial_bitmask=polynomial,
                polynomial_basis=[1 << i for i in range(n)],
                encoding='integer bit i is coefficient of X^i; table index is standard polynomial-basis encoding')


def polynomial_table(spec, trace=False, max_work=2_000_000):
    n, N, polynomial = validate_field(spec, {'n', 'polynomial', 'terms'})
    terms = spec.get('terms')
    if type(terms) is not list or len(terms) > MAX_TERMS:
        raise FieldError(f'terms must be a list with at most {MAX_TERMS} explicit terms')
    for i, term in enumerate(terms):
        if type(term) is not dict or set(term) != {'coefficient', 'exponent'}:
            raise FieldError(f'term {i} needs exactly coefficient and exponent')
        integer(term['coefficient'], f'term {i} coefficient', 0, N-1)
        integer(term['exponent'], f'term {i} exponent', 0, MAX_EXPONENT)
    estimated = N * n * sum(2*max(1,t['exponent'].bit_length()) + 1 for t in terms)
    if trace:
        estimated += N*n*n
    limits = budget(estimated, max_work)
    field_values = []
    for x in range(N):
        value = 0
        for term in terms:
            # gf_pow(0,0)=1 is deliberate: X^0 is the constant polynomial 1.
            value ^= gf_mul(term['coefficient'], gf_pow(x,term['exponent'],polynomial),polynomial)
        field_values.append(value)
    table = [absolute_trace(y,n,polynomial) for y in field_values] if trace else field_values
    m = 1 if trace else n
    result = dict(schema_version=1, status='exact_finite_construction',
                  operation='trace' if trace else 'polynomial', input=spec,
                  n=n, m=m, table=table, field=field_metadata(n,polynomial),
                  construction=dict(formula='Tr(sum_i c_i*x^e_i)' if trace else 'sum_i c_i*x^e_i',
                                    addition='XOR in the field', constant_convention='0^0=1 for exponent-zero terms',
                                    exponent_reduction='evaluated exactly, not reduced modulo 2^n-1 at x=0',
                                    terms=terms), budget=limits,
                  limitation='Finite table generation only; no novelty, spectral, differential, or security claim. Analyze the returned table separately.')
    if trace:
        result['pre_trace_field_values'] = field_values
    return result


def dual_basis(spec, max_work=2_000_000):
    n, N, polynomial = validate_field(spec, {'n', 'polynomial', 'basis'})
    basis = spec.get('basis', [1 << i for i in range(n)])
    if type(basis) is not list or len(basis) != n:
        raise FieldError('basis must contain exactly n field-element encodings')
    for i,x in enumerate(basis):
        integer(x, f'basis[{i}]', 0, N-1)
    if basis_rank(basis) != n:
        raise FieldError('basis must be F2-linearly independent')
    limits = budget(N*n*n*n + N*n*n, max_work)
    # Compute pairing columns once. Nondegeneracy gives each coordinate unit vector
    # exactly one preimage; check uniqueness rather than merely finding a match.
    pairing_map = {}
    for candidate in range(N):
        signature = sum(absolute_trace(gf_mul(beta,candidate,polynomial),n,polynomial) << i
                        for i,beta in enumerate(basis))
        if signature in pairing_map:
            raise AssertionError('trace pairing unexpectedly degenerate')
        pairing_map[signature] = candidate
    dual = [pairing_map[1 << i] for i in range(n)]
    matrix = [[absolute_trace(gf_mul(beta,d,polynomial),n,polynomial) for d in dual]
              for beta in basis]
    assert matrix == [[int(i==j) for j in range(n)] for i in range(n)]
    # This table maps standard polynomial-basis encodings to coordinates in basis.
    coordinates = [sum(absolute_trace(gf_mul(x,d,polynomial),n,polynomial) << i
                       for i,d in enumerate(dual)) for x in range(N)]
    for x, coord in enumerate(coordinates):
        reconstructed = 0
        for i,beta in enumerate(basis):
            if coord >> i & 1:
                reconstructed ^= beta
        assert reconstructed == x
    return dict(schema_version=1,status='exact_trace_pairing',operation='dual-basis',input=spec,
                field=field_metadata(n,polynomial),basis=basis,dual_basis=dual,
                pairing_matrix=matrix,standard_to_basis_coordinates=coordinates,
                reconstruction='x = XOR_i Tr(x*dual_basis[i])*basis[i]',
                budget=limits,
                limitation='Basis elements and duals are encoded in the standard polynomial basis; the coordinates table is explicitly in the requested basis. This does not silently change construction-table indexing.')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['polynomial','trace','dual-basis'])
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--max-work',type=int,default=2_000_000)
    args=parser.parse_args(argv)
    try:
        if args.input.resolve()==args.out.resolve():
            raise FieldError('output must not overwrite input')
        spec=json.loads(args.input.read_text(encoding='utf-8-sig'))
        if args.operation=='dual-basis':
            result=dual_basis(spec,args.max_work)
        else:
            result=polynomial_table(spec,args.operation=='trace',args.max_work)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    except (FieldError,OSError,json.JSONDecodeError) as exc:
        print(f'error: {exc}',file=sys.stderr)
        return 2
    print(json.dumps(dict(status=result['status'],operation=args.operation,out=str(args.out)),ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
