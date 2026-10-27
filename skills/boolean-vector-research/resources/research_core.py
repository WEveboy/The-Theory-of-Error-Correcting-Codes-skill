"""Exact, bounded Boolean/vectorial research calculations (Python 3.10+).

Integers encode bit vectors with coordinate x_i in bit i. Table[x] is F(x).
All counts and transforms are integer exact. No novelty/equivalence claim.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

VERSION = "0.2.0"
MAX_SPECTRUM_ENTRIES = 1_000_000


class ResearchError(ValueError):
    pass


def integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ResearchError(f"{name} must be an integer in [{minimum}, {maximum}] (booleans rejected)")
    return value


def parity(value):
    return value.bit_count() & 1


def fwht(values):
    """Unnormalized Walsh-Hadamard transform; returns a new integer list."""
    if not values or len(values) & (len(values) - 1):
        raise ResearchError("FWHT length must be a positive power of two")
    out = list(values)
    size = 1
    while size < len(out):
        for start in range(0, len(out), 2 * size):
            for j in range(start, start + size):
                a, b = out[j], out[j + size]
                out[j], out[j + size] = a + b, a - b
        size *= 2
    return out


def anf_coefficients(table):
    """Subset Mobius transform over F_2, also its own inverse."""
    out = list(table)
    n = (len(out) - 1).bit_length()
    for i in range(n):
        for s in range(len(out)):
            if s & (1 << i):
                out[s] ^= out[s ^ (1 << i)]
    return out


def gf2_basis(rows):
    """Independent row basis indexed by highest nonzero bit."""
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in basis:
                basis[p] = row
                break
            row ^= basis[p]
    return basis


def gf2_null_vector(rows, columns):
    basis = gf2_basis(rows)
    free = next((j for j in range(columns) if j not in basis), None)
    if free is None:
        return None
    result = 1 << free
    for p in sorted(basis):
        if parity((basis[p] ^ (1 << p)) & result):
            result |= 1 << p
    return result


def truth_word(table):
    return sum(bit << x for x, bit in enumerate(table))


def algebraic_immunity(table):
    """Exact minimum-degree annihilator of f or f+1; n<=6 only."""
    n = (len(table) - 1).bit_length()
    if n > 6:
        return {"status": "not_computed", "reason": "exact AI restricted to n<=6"}
    for d in range((n + 1) // 2 + 1):
        masks = [s for s in range(len(table)) if s.bit_count() <= d]
        # g vanishes on support(f+side), so (f+side)*g=0.
        for side in (0, 1):
            rows = [sum(int(x & s == s) << j for j, s in enumerate(masks))
                    for x in range(len(table)) if table[x] ^ side]
            solution = gf2_null_vector(rows, len(masks))
            if solution is not None:
                monomials = [s for j, s in enumerate(masks) if solution >> j & 1]
                g = [sum(int(x & s == s) for s in monomials) % 2
                     for x in range(len(table))]
                if not any(g) or any((table[x] ^ side) & g[x] for x in range(len(table))):
                    raise AssertionError("invalid annihilator certificate")
                return {"status": "exact", "value": d,
                        "annihilates": "f" if side == 0 else "f+1",
                        "witness_anf_monomial_masks": monomials,
                        "witness_table": g,
                        "minimality": "all lower-degree homogeneous systems had full column rank"}
    raise AssertionError("AI bound violated")


def second_order_nonlinearity(table):
    n = (len(table) - 1).bit_length()
    if n > 4:
        return {"status": "not_computed", "reason": "exact RM(2,n) enumeration restricted to n<=4"}
    masks = [s for s in range(len(table)) if s.bit_count() <= 2]
    rows = [truth_word([int(x & s == s) for x in range(len(table))]) for s in masks]
    target = truth_word(table)
    best, best_coeffs, best_word = len(table) + 1, 0, 0
    word, previous_gray = 0, 0
    for index in range(1 << len(rows)):
        gray = index ^ (index >> 1)
        if index:
            changed = gray ^ previous_gray
            word ^= rows[changed.bit_length() - 1]
        distance = (target ^ word).bit_count()
        if distance < best:
            best, best_coeffs, best_word = distance, gray, word
        previous_gray = gray
    return {"status": "exact", "order": 2, "value": best,
            "nearest_anf_monomial_masks": [s for j, s in enumerate(masks) if best_coeffs >> j & 1],
            "nearest_table": [(best_word >> x) & 1 for x in range(len(table))],
            "method": "complete enumeration of RM(2,n)"}


def component_report(table, n, mask, advanced=False):
    N = len(table)
    anf = anf_coefficients(table)
    monomials = [s for s, value in enumerate(anf) if value]
    degree = max((s.bit_count() for s in monomials), default=-1)
    spectrum = fwht([1 - 2 * v for v in table])
    assert sum(w * w for w in spectrum) == N * N
    amplitude = max(map(abs, spectrum))
    frequency = next(a for a, w in enumerate(spectrum) if abs(w) == amplitude)
    constant = int(spectrum[frequency] < 0)
    nearest_distance = sum(table[x] ^ parity(frequency & x) ^ constant for x in range(N))
    nl = (N - amplitude) // 2
    assert nearest_distance == nl
    ac_numerators = fwht([w * w for w in spectrum])
    assert all(v % N == 0 for v in ac_numerators)
    autocorrelation = [v // N for v in ac_numerators]
    nonzero_low = [a.bit_count() for a in range(1, N) if spectrum[a]]
    ci = min(nonzero_low) - 1 if nonzero_low else n
    bent = n % 2 == 0 and all(abs(w) == 1 << (n // 2) for w in spectrum)
    coset = Counter((N - sign * w) // 2 for w in spectrum for sign in (-1, 1))
    report = {"mask": mask, "weight": sum(table), "degree": degree,
              "degree_convention": "zero function has degree -1; nonzero constant has degree 0",
              "anf_monomial_masks": monomials, "walsh": spectrum,
              "walsh_histogram": dict(sorted(Counter(spectrum).items())),
              "maximum_absolute_walsh": amplitude, "nonlinearity": nl,
              "nearest_affine": {"linear_mask": frequency, "constant": constant, "distance": nl},
              "balanced": spectrum[0] == 0, "bent": bent,
              "plateaued": len({abs(w) for w in spectrum if w}) == 1,
              "rm1_coset_weight_distribution": dict(sorted(coset.items())),
              "autocorrelation": autocorrelation,
              "absolute_indicator": max(abs(v) for v in autocorrelation[1:]),
              "sum_of_squares_indicator": sum(v * v for v in autocorrelation),
              "correlation_immunity_order": ci,
              "correlation_immunity_convention": "largest t<=n with W(a)=0 for 1<=wt(a)<=t; constants have t=n",
              "resiliency_order": ci if spectrum[0] == 0 else None,
              "linear_structures": [{"direction": u, "derivative_constant": int(autocorrelation[u] < 0)}
                                    for u in range(1, N) if abs(autocorrelation[u]) == N]}
    if degree <= 2:
        rows = [sum((table[(1 << i) ^ (1 << j)] ^ table[1 << i] ^ table[1 << j] ^ table[0]) << j
                    for j in range(n)) for i in range(n)]
        rank = len(gf2_basis(rows))
        assert rank % 2 == 0
        predicted = 1 << (n - rank // 2)
        assert {abs(w) for w in spectrum if w} == {predicted}
        assert sum(w != 0 for w in spectrum) == 1 << rank
        radical = [u for u in range(N) if all(parity(row & u) == 0 for row in rows)]
        report["quadratic_polar"] = {"status": "applicable", "rows_as_bitmasks": rows,
                                      "rank": rank, "radical": radical,
                                      "predicted_nonzero_walsh_magnitude": predicted,
                                      "predicted_nonzero_walsh_count": 1 << rank,
                                      "prediction_matches_exact_spectrum": True}
    else:
        report["quadratic_polar"] = {"status": "not_applicable", "reason": "degree exceeds 2"}
    if advanced:
        report["algebraic_immunity"] = algebraic_immunity(table)
        report["second_order_nonlinearity"] = second_order_nonlinearity(table)
    return report


def code_report(table, n, m, nonlinearity):
    N = len(table)
    rows = [(1 << N) - 1]
    rows += [truth_word([(x >> i) & 1 for x in range(N)]) for i in range(n)]
    rows += [truth_word([(y >> j) & 1 for y in table]) for j in range(m)]
    independent = list(gf2_basis(rows).values())
    rank = len(independent)
    full = rank == n + m + 1
    if not full:
        assert nonlinearity == 0
    report = {"length": N, "rank": rank, "number_of_words": 1 << rank,
              "expected_full_rank": n + m + 1, "full_rank_bridge_applicable": full,
              "generator_row_order": "1,x_0,...,x_(n-1),F_0,...,F_(m-1)",
              "generator_rows_hex": [hex(row) for row in rows],
              "bridge_explanation": ("full rank: minimum nonzero code weight equals NL(F)" if full else
                 "rank deficient: some nonzero output component is affine, hence NL(F)=0; minimum positive code weight cannot substitute for NL(F)")}
    if rank <= 16 and N <= 256:
        distribution = Counter()
        word, previous = 0, 0
        for i in range(1 << rank):
            gray = i ^ (i >> 1)
            if i:
                word ^= independent[(gray ^ previous).bit_length() - 1]
            distribution[word.bit_count()] += 1
            previous = gray
        minimum = min(w for w in distribution if w)
        if full:
            assert minimum == nonlinearity
        report.update(enumeration_status="exact", minimum_positive_weight=minimum,
                      weight_distribution=dict(sorted(distribution.items())))
    else:
        report.update(enumeration_status="not_computed",
                      reason="complete code enumeration restricted to rank<=16 and length<=256",
                      minimum_positive_weight=nonlinearity if full else None,
                      minimum_weight_method="full-rank theorem" if full else "not_computed")
    return report


def validate_spec(spec, max_n=8, max_work=25_000_000, advanced=False):
    integer(max_n, "max_n", 1, 12)
    integer(max_work, "max_work", 1, 1_000_000_000)
    if type(spec) is not dict:
        raise ResearchError("input must be a JSON object")
    n = integer(spec.get("n"), "n", 1, max_n)
    m = integer(spec.get("m"), "m", 1, n)
    table = spec.get("table")
    N = 1 << n
    if type(table) is not list or len(table) != N:
        raise ResearchError(f"table must contain exactly 2^n={N} integer values")
    for i, y in enumerate(table):
        integer(y, f"table[{i}]", 0, (1 << m) - 1)
    entries = N * ((1 << m) - 1)
    if entries > MAX_SPECTRUM_ENTRIES:
        raise ResearchError(f"all-component spectrum exceeds {MAX_SPECTRUM_ENTRIES} entries; use structural proofs")
    # Work is an explicit conservative estimate, not a timing promise.
    work = entries * (3 * n + 4) + N * (N - 1)
    if advanced and n <= 6:
        work += ((1 << m) - 1) * 2 * ((n + 1) // 2 + 1) * N * N
    if advanced and n <= 4:
        work += ((1 << m) - 1) * (1 << (1 + n + math.comb(n, 2)))
    if work > max_work:
        raise ResearchError(f"estimated work {work} exceeds max_work={max_work}; raise budget explicitly or reduce input")
    return n, m, table, work


def analyze(spec, max_n=8, max_work=25_000_000, advanced=False, include_ddt=False):
    n, m, table, work = validate_spec(spec, max_n, max_work, advanced)
    N, M = 1 << n, 1 << m
    components = [component_report([parity(b & y) for y in table], n, b, advanced)
                  for b in range(1, M)]
    nl = min(c["nonlinearity"] for c in components)
    all_quadratic = all(c["degree"] <= 2 for c in components)
    delta, delta_u, delta_v = 0, None, None
    rows_out, ddt_hist, structures, derivative_ranks = [], Counter(), [], []
    for u in range(1, N):
        counts = [0] * M
        for x in range(N):
            counts[table[x] ^ table[x ^ u]] += 1
        assert sum(counts) == N and all(v % 2 == 0 for v in counts)
        value = max(counts)
        if value > delta:
            delta, delta_u, delta_v = value, u, counts.index(value)
        if value == N:
            structures.append({"direction": u, "derivative_constant": counts.index(value)})
        ddt_hist.update(counts)
        if include_ddt:
            rows_out.append({"direction": u, "counts": counts})
        if all_quadratic:
            base = table[u] ^ table[0]
            columns = [table[u ^ (1 << i)] ^ table[1 << i] ^ base for i in range(n)]
            rank = len(gf2_basis(columns))
            assert value == 1 << (n - rank)
            derivative_ranks.append({"direction": u, "rank": rank, "kernel_dimension": n - rank,
                                     "nonempty_fiber_size": 1 << (n - rank)})
    outputs = [table.count(y) for y in range(M)]
    canonical = json.dumps({"n": n, "m": m, "table": table}, separators=(",", ":"))
    report = {"schema_version": 1, "tool_version": VERSION, "status": "exact_finite_analysis",
              "input": spec, "truth_table_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
              "representation": "integer order; bit i is coordinate x_i; XOR addition; unnormalized integer Walsh",
              "metadata_status": "optional field/basis metadata recorded verbatim, not algebraically certified",
              "budget": {"max_n": max_n, "max_work": max_work, "estimated_work_units": work,
                         "advanced_requested": advanced, "ddt_rows_requested": include_ddt},
              "n": n, "m": m, "length": N, "components": components,
              "degree": max(c["degree"] for c in components), "nonlinearity": nl,
              "worst_component_mask": next(c["mask"] for c in components if c["nonlinearity"] == nl),
              "balanced": all(count == N // M for count in outputs),
              "output_counts": outputs, "permutation": n == m and len(set(table)) == N,
              "vectorial_bent": all(c["bent"] for c in components),
              "differential_uniformity": delta,
              "apn": delta == 2 if n == m else None,
              "apn_convention": "APN flag restricted to square n->n functions",
              "worst_differential": {"direction": delta_u, "difference": delta_v, "count": delta,
                                      "input_witnesses": [x for x in range(N) if table[x] ^ table[x ^ delta_u] == delta_v]},
              "ddt_entry_histogram_nonzero_directions": dict(sorted(ddt_hist.items())),
              "linear_structures": structures,
              "quadratic_derivatives": {"status": "applicable", "directions": derivative_ranks}
                   if all_quadratic else {"status": "not_applicable", "reason": "vector degree exceeds 2"},
              "generated_code": code_report(table, n, m, nl),
              "limits": ["finite input only; no new-family or optimality claim",
                         "no EA/CCZ equivalence decision or literature novelty verification",
                         "optional metadata alone does not certify the field model"]}
    if include_ddt:
        report["ddt_nonzero_direction_rows"] = rows_out
    return report


def gf_mul(a, b, polynomial):
    n = polynomial.bit_length() - 1
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= polynomial
    return result


def gf_pow(a, exponent, polynomial):
    result = 1
    while exponent:
        if exponent & 1:
            result = gf_mul(result, a, polynomial)
        a = gf_mul(a, a, polynomial)
        exponent >>= 1
    return result


def polynomial_remainder(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def is_irreducible(polynomial, n):
    if polynomial.bit_length() != n + 1 or polynomial & 1 == 0:
        return False
    # Trial divisors suffice for n<=12; independent of multiplication tables.
    for degree in range(1, n // 2 + 1):
        for divisor in range((1 << degree) | 1, 1 << (degree + 1), 2):
            if polynomial_remainder(polynomial, divisor) == 0:
                return False
    return True


def construct_spec(family, n, pi=None, g=None, k=1, polynomial=None):
    integer(n, "n", 1, 12)
    if family in ("quadratic-bent", "mm"):
        if k != 1 or polynomial is not None:
            raise ResearchError("k and polynomial are parameters of the Gold family only")
        if n % 2:
            raise ResearchError("bent constructions require even n")
        if family == "quadratic-bent":
            if pi is not None or g is not None:
                raise ResearchError("pi and g are parameters of the MM family only")
            table = [parity(sum((((x >> i) & 1) & ((x >> (i + 1)) & 1)) << (i // 2)
                                for i in range(0, n, 2))) for x in range(1 << n)]
            return {"n": n, "m": 1, "table": table,
                    "construction": {"family": family, "formula": "sum_i x_(2i)*x_(2i+1) over F2"}}
        khalf, size = n // 2, 1 << (n // 2)
        pi = list(range(size)) if pi is None else pi
        g = [0] * size if g is None else g
        if type(pi) is not list or len(pi) != size or any(type(v) is not int for v in pi) or sorted(pi) != list(range(size)):
            raise ResearchError("MM pi must be a permutation list of 0..2^(n/2)-1")
        if type(g) is not list or len(g) != size or any(type(v) is not int or v not in (0, 1) for v in g):
            raise ResearchError("MM g must be a binary table of length 2^(n/2)")
        table = [parity((x & (size - 1)) & pi[x >> khalf]) ^ g[x >> khalf] for x in range(1 << n)]
        return {"n": n, "m": 1, "table": table,
                "construction": {"family": family, "formula": "u dot pi(v) + g(v)",
                                 "u_bits": "low n/2 bits", "pi": pi, "g": g}}
    if family == "gold":
        if pi is not None or g is not None:
            raise ResearchError("pi and g are parameters of the MM family only")
        if n < 2:
            raise ResearchError("Gold constructor requires n>=2")
        integer(k, "k", 1, n - 1)
        if math.gcd(k, n) != 1:
            raise ResearchError("Gold APN constructor requires gcd(k,n)=1")
        if polynomial is None:
            polynomial = next(p for p in range((1 << n) | 1, 1 << (n + 1), 2) if is_irreducible(p, n))
        integer(polynomial, "polynomial", 1 << n, (1 << (n + 1)) - 1)
        if not is_irreducible(polynomial, n):
            raise ResearchError("polynomial must be irreducible of degree n over F2")
        exponent = (1 << k) + 1
        return {"n": n, "m": n, "table": [gf_pow(x, exponent, polynomial) for x in range(1 << n)],
                "field": {"irreducible_polynomial_bitmask": polynomial, "basis": "polynomial basis, least significant coefficient first"},
                "construction": {"family": family, "k": k, "exponent": exponent,
                                 "condition": "gcd(k,n)=1", "permutation_condition": "n odd"}}
    raise ResearchError(f"unsupported family: {family}")


def demo_spec(case):
    if case == "scalar-bent":
        return construct_spec("quadratic-bent", 4)
    if case == "vector-bent":
        return {"n": 4, "m": 2, "table": [gf_mul(z & 3, z >> 2, 0b111) for z in range(16)],
                "field": {"irreducible_polynomial_bitmask": 7, "basis": "GF4 polynomial basis"},
                "construction": {"formula": "GF4 product xy; low two bits x, upper two bits y"}}
    if case == "apn-cube":
        return construct_spec("gold", 3, k=1, polynomial=0b1011)
    if case == "identity":
        return {"n": 3, "m": 3, "table": list(range(8)), "construction": {"formula": "F(x)=x"}}
    raise ResearchError(f"unsupported demo: {case}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "construct", "demo"):
        p = sub.add_parser(command)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--max-n", type=int, default=8)
        p.add_argument("--max-work", type=int, default=25_000_000)
        p.add_argument("--advanced", action="store_true")
        p.add_argument("--include-ddt", action="store_true")
        if command == "analyze":
            p.add_argument("--input", type=Path, required=True)
        elif command == "construct":
            p.add_argument("--family", choices=("quadratic-bent", "mm", "gold"), required=True)
            p.add_argument("--n", type=int, required=True)
            p.add_argument("--params", type=Path, help="JSON with pi,g for MM or k,polynomial for Gold")
        else:
            p.add_argument("--case", choices=("scalar-bent", "vector-bent", "apn-cube", "identity"), required=True)
    args = parser.parse_args(argv)
    try:
        source_path = getattr(args, 'input', None) or getattr(args, 'params', None)
        if source_path is not None and source_path.resolve() == args.out.resolve():
            raise ResearchError('output must not overwrite the input or constructor parameters')
        if args.command == "analyze":
            spec = json.loads(args.input.read_text(encoding="utf-8-sig"))
        elif args.command == "construct":
            params = json.loads(args.params.read_text(encoding="utf-8-sig")) if args.params else {}
            if type(params) is not dict:
                raise ResearchError("constructor params must be a JSON object")
            if set(params) - {"pi", "g", "k", "polynomial"}:
                raise ResearchError("unknown constructor parameter")
            allowed = {'mm': {'pi', 'g'}, 'gold': {'k', 'polynomial'}, 'quadratic-bent': set()}[args.family]
            if set(params) - allowed:
                raise ResearchError(f"parameters not supported by {args.family}: {sorted(set(params) - allowed)}")
            # Check input dimensions before allocating a constructed table.
            integer(args.n, "n", 1, integer(args.max_n, "max_n", 1, 12))
            spec = construct_spec(args.family, args.n, **params)
        else:
            spec = demo_spec(args.case)
        report = analyze(spec, args.max_n, args.max_work, args.advanced, args.include_ddt)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except (ResearchError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "out": str(args.out),
                      "nonlinearity": report["nonlinearity"],
                      "differential_uniformity": report["differential_uniformity"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
