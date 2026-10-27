"""Exact finite combinatorial checks; no existence or novelty assertions.

python research_extensions.py {ea,macwilliams,oa,design,sequence} --input spec.json --out result.json
All counts use integers/Fraction. Invalid input returns exit 2 without a success report.
"""
import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path


def integer(x, low=0, high=None):
    if type(x) is not int or x < low or (high is not None and x > high):
        raise ValueError(f'Expected integer in [{low}, {high}], got {x!r}')
    return x


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def linear(rows, x):
    return sum(((r & x).bit_count() & 1) << i for i, r in enumerate(rows))


def ea(spec):
    n, m = integer(spec['n'], 1, 10), integer(spec['m'], 1, 10)
    table = spec['table']
    if not isinstance(table, list) or len(table) != 1 << n:
        raise ValueError('table length must be 2**n')
    for y in table:
        integer(y, 0, (1 << m) - 1)
    A = spec.get('input_rows', [1 << i for i in range(n)])
    B = spec.get('output_rows', [1 << i for i in range(m)])
    L = spec.get('affine_rows', [0] * m)
    for rows, count, limit in [(A, n, 1 << n), (B, m, 1 << m), (L, m, 1 << n)]:
        if not isinstance(rows, list) or len(rows) != count:
            raise ValueError('matrix row count mismatch')
        for r in rows:
            integer(r, 0, limit - 1)
    if rank(A) != n or rank(B) != m:
        raise ValueError('input/output matrices must be invertible for EA certificate')
    shift = integer(spec.get('input_shift', 0), 0, (1 << n) - 1)
    const = integer(spec.get('output_constant', 0), 0, (1 << m) - 1)
    transformed = [linear(B, table[linear(A, x) ^ shift]) ^ linear(L, x) ^ const for x in range(1 << n)]
    target = spec.get('target')
    if target is not None:
        if not isinstance(target, list) or len(target) != 1 << n:
            raise ValueError('target length must be 2**n')
        for y in target:
            integer(y, 0, (1 << m) - 1)
    return dict(status='exact', convention='G(x)=B F(Ax+s)+Lx+c over F2', n=n, m=m,
                table=transformed, matches_target=None if target is None else target == transformed,
                certificate=dict(input_rows=A, output_rows=B, affine_rows=L,
                                 input_shift=shift, output_constant=const),
                limitation='Verifies this EA map only; does not search or certify inequivalence. EA need not preserve permutation.')


def krawtchouk(N, k, i):
    return sum((-1) ** j * math.comb(i, j) * math.comb(N-i, k-j)
               for j in range(max(0, k-(N-i)), min(k, i)+1))


def macwilliams(spec):
    N = integer(spec['length'], 1, 512)
    raw = spec['distribution']
    if not isinstance(raw, dict):
        raise ValueError('distribution must map decimal weights to nonnegative integer counts')
    dist = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not key.isascii() or not key.isdigit() or str(int(key)) != key:
            raise ValueError('weight keys must be canonical decimal integers')
        i = integer(int(key), 0, N)
        dist[i] = integer(value)
    size = sum(dist.values())
    if dist.get(0) != 1 or not size or size & (size-1):
        raise ValueError('a putative binary linear weight distribution needs A0=1 and power-of-two size')
    if (N + 1) * N * len(dist) > 5_000_000:
        raise ValueError('MacWilliams exact-computation budget exceeded; reduce length or support')
    values = [Fraction(sum(v * krawtchouk(N, k, i) for i, v in dist.items()), size)
              for k in range(N+1)]
    valid = all(v.denominator == 1 and v >= 0 for v in values)
    return dict(status='necessary_conditions_only', length=N, size=size,
                transform={str(i): int(v) if v.denominator == 1 else str(v) for i, v in enumerate(values) if v},
                nonnegative_integers=valid,
                limitation='Input enumerator is not evidence that a linear code exists. This is the binary linear MacWilliams transform, not a nonlinear dual.')


def oa(spec):
    rows = spec['rows']
    if not isinstance(rows, list) or not rows or len(rows) > 65536:
        raise ValueError('rows must be nonempty with <=65536 entries')
    if not isinstance(rows[0], list):
        raise ValueError('each row must be a bit list')
    n = integer(len(rows[0]), 1, 64)
    t = integer(spec['strength'], 0, min(n, 4))
    for row in rows:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError('rows must have the same width')
        for x in row:
            integer(x, 0, 1)
    if math.comb(n, t) * len(rows) > 10_000_000:
        raise ValueError('projection-check budget exceeded')
    M = len(rows)
    if M % (1 << t):
        return dict(status='exact', is_orthogonal_array=False, reason='row count not divisible by 2**strength')
    expected = M // (1 << t)
    for cols in itertools.combinations(range(n), t):
        counts = Counter(tuple(r[c] for c in cols) for r in rows)
        for pattern in itertools.product((0, 1), repeat=t):
            if counts[pattern] != expected:
                return dict(status='exact', is_orthogonal_array=False,
                            witness=dict(columns=cols, pattern=pattern, count=counts[pattern], expected=expected))
    return dict(status='exact', is_orthogonal_array=True, rows=M, width=n, strength=t, index=expected,
                repeated_rows='allowed; this checks the multiset supplied')


def design(spec):
    v = integer(spec['v'], 1, 64)
    k = integer(spec['k'], 0, v)
    t = integer(spec['t'], 0, min(k, 4))
    raw = spec['blocks']
    if not isinstance(raw, list) or not raw or len(raw) > 65536:
        raise ValueError('blocks must be nonempty list of coordinate lists')
    blocks = []
    for block in raw:
        if not isinstance(block, list) or len(block) != k:
            raise ValueError('all blocks must have k distinct coordinates')
        for x in block:
            integer(x, 0, v-1)
        if len(set(block)) != k:
            raise ValueError('duplicate coordinate in block')
        blocks.append(frozenset(block))
    if len(set(blocks)) != len(blocks):
        raise ValueError('this command accepts simple designs only: duplicate blocks rejected')
    work = len(blocks) * math.comb(k, t) + math.comb(v, t)
    if work > 10_000_000:
        raise ValueError('design-check budget exceeded')
    lam = Fraction(len(blocks) * math.comb(k, t), math.comb(v, t))
    counts = Counter(s for b in blocks for s in itertools.combinations(sorted(b), t))
    for subset in itertools.combinations(range(v), t):
        if counts[subset] != lam:
            return dict(status='exact', is_design=False, proposed_lambda=str(lam),
                        witness=dict(subset=subset, count=counts[subset]))
    return dict(status='exact', is_design=True, v=v, k=k, t=t, blocks=len(blocks), lambda_value=int(lam))


def sequence(spec):
    a, b = spec['sequence'], spec.get('other', spec['sequence'])
    if not isinstance(a, list) or not a or len(a) > 4096 or not isinstance(b, list) or len(b) != len(a):
        raise ValueError('sequences must have equal length in 1..4096')
    for x in a+b:
        integer(x, 0, 1)
    group = spec.get('shift_group')
    if group not in ('cyclic', 'xor'):
        raise ValueError('explicit shift_group must be cyclic or xor')
    N = len(a)
    if group == 'xor' and N & (N-1):
        raise ValueError('xor shift needs power-of-two length')
    corr = [sum(1-2*(a[x]^b[(x+u) % N if group == 'cyclic' else x ^ u]) for x in range(N)) for u in range(N)]
    return dict(status='exact', shift_group=group, correlation=corr,
                convention='sum_x (-1)^(a[x]+b[shift(x,u)]); indices start at 0',
                maximum_absolute_nonzero_shift=max(map(abs, corr[1:]), default=0))


OPERATIONS = dict(ea=ea, macwilliams=macwilliams, oa=oa, design=design, sequence=sequence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=OPERATIONS)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        spec = json.loads(args.input.read_text(encoding='utf-8-sig'))
        if not isinstance(spec, dict):
            raise ValueError('input must be a JSON object')
        result = OPERATIONS[args.operation](spec)
        if args.input.resolve() == args.out.resolve():
            raise ValueError('output must not overwrite input')
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(dict(status='ok', operation=args.operation, output=str(args.out)), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f'Input/operation error: {exc}\n')


if __name__ == '__main__':
    main()
