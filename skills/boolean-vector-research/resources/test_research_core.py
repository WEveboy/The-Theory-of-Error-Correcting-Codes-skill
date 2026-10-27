"""Run with: python test_research_core.py (standard library only)."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

import research_core as core


def direct_walsh(t):
    return [sum((-1) ** (t[x] ^ ((a & x).bit_count() % 2)) for x in range(len(t)))
            for a in range(len(t))]


def direct_ac(t):
    return [sum((-1) ** (t[x] ^ t[x ^ u]) for x in range(len(t)))
            for u in range(len(t))]


def evaluate_anf(masks, n):
    return [sum(int(x & s == s) for s in masks) % 2 for x in range(1 << n)]


def direct_ai(t):
    n = (len(t) - 1).bit_length()
    # Exhaustive nonzero function oracle, independent of the linear-system algorithm.
    for d in range(n + 1):
        for bits in range(1, 1 << len(t)):
            g = [(bits >> x) & 1 for x in range(len(t))]
            a = core.anf_coefficients(g)
            if max((s.bit_count() for s, v in enumerate(a) if v), default=-1) != d:
                continue
            if all(not (t[x] & g[x]) for x in range(len(t))) or all(not ((1 ^ t[x]) & g[x]) for x in range(len(t))):
                return d
    raise AssertionError


class TransformTests(unittest.TestCase):
    def test_fwht_against_direct_definition(self):
        rng = random.Random(20261027)
        for n in range(1, 7):
            for _ in range(5):
                t = [rng.randrange(2) for _ in range(1 << n)]
                self.assertEqual(core.fwht([1 - 2 * x for x in t]), direct_walsh(t))

    def test_transform_involution(self):
        x = [3, -5, 0, 19, -1, 6, 12, 0]
        self.assertEqual(core.fwht(core.fwht(x)), [len(x) * v for v in x])
        with self.assertRaises(core.ResearchError):
            core.fwht([1, 2, 3])

    def test_anf_roundtrip_and_direct_polynomial(self):
        rng = random.Random(7)
        for n in range(1, 7):
            t = [rng.randrange(2) for _ in range(1 << n)]
            a = core.anf_coefficients(t)
            self.assertEqual(core.anf_coefficients(a), t)
            self.assertEqual(evaluate_anf([s for s, v in enumerate(a) if v], n), t)

    def test_gf2_basis_against_exhaustive_row_span(self):
        for rows in ([1, 2, 3], [0, 0], [5, 3, 6], [0b1110, 0b0101, 0b1011, 0b1001]):
            span = {0}
            for row in rows:
                span |= {v ^ row for v in list(span)}
            self.assertEqual(1 << len(core.gf2_basis(rows)), len(span))

    def test_null_vector(self):
        for columns in range(1, 5):
            for rows in ([0], [1], [1, 2], [3, 5, 6], list(range(1 << columns))):
                rows = [r & ((1 << columns) - 1) for r in rows]
                solution = core.gf2_null_vector(rows, columns)
                oracle = [x for x in range(1, 1 << columns) if all((r & x).bit_count() % 2 == 0 for r in rows)]
                self.assertEqual(solution is None, not oracle)
                if solution is not None:
                    self.assertIn(solution, oracle)


class MathematicalTests(unittest.TestCase):
    def test_scalar_bent_example(self):
        r = core.analyze(core.demo_spec("scalar-bent"), advanced=True)
        c = r['components'][0]
        self.assertEqual((r['nonlinearity'], r['degree'], c['quadratic_polar']['rank']), (6, 2, 4))
        self.assertTrue(r['vectorial_bent'])
        self.assertFalse(r['balanced'])
        self.assertEqual(c['rm1_coset_weight_distribution'], {6: 16, 10: 16})
        self.assertEqual(r['generated_code']['weight_distribution'], {0: 1, 6: 16, 8: 30, 10: 16, 16: 1})
        self.assertEqual(c['autocorrelation'], [16] + [0] * 15)
        self.assertEqual(c['second_order_nonlinearity']['value'], 0)

    def test_vector_bent_product(self):
        r = core.analyze(core.demo_spec("vector-bent"), include_ddt=True)
        self.assertEqual((r['nonlinearity'], r['differential_uniformity']), (6, 4))
        self.assertEqual(r['output_counts'], [7, 3, 3, 3])
        self.assertTrue(all(c['bent'] for c in r['components']))
        self.assertTrue(all(d['rank'] == 2 for d in r['quadratic_derivatives']['directions']))
        self.assertEqual(len(r['ddt_nonzero_direction_rows']), 15)

    def test_apn_cube(self):
        r = core.analyze(core.demo_spec("apn-cube"), advanced=True)
        self.assertTrue(r['permutation'])
        self.assertTrue(r['balanced'])
        self.assertTrue(r['apn'])
        self.assertEqual((r['nonlinearity'], r['differential_uniformity']), (2, 2))
        self.assertTrue(all(c['degree'] == 2 for c in r['components']))
        self.assertFalse(r['vectorial_bent'])

    def test_rank_degeneracy(self):
        r = core.analyze(core.demo_spec("identity"))
        self.assertEqual(r['nonlinearity'], 0)
        self.assertEqual(r['generated_code']['rank'], 4)
        self.assertEqual(r['generated_code']['minimum_positive_weight'], 4)
        self.assertFalse(r['generated_code']['full_rank_bridge_applicable'])
        self.assertEqual(r['differential_uniformity'], 8)
        self.assertEqual(len(r['linear_structures']), 7)

    def test_coordinate_bent_does_not_imply_vector_bent(self):
        q = core.demo_spec("scalar-bent")['table']
        t = [q[x] | ((q[x] ^ (x & 1)) << 1) for x in range(16)]
        r = core.analyze({'n': 4, 'm': 2, 'table': t})
        self.assertTrue(r['components'][0]['bent'])
        self.assertTrue(r['components'][1]['bent'])
        self.assertFalse(r['components'][2]['bent'])
        self.assertEqual(r['components'][2]['degree'], 1)
        self.assertEqual(r['nonlinearity'], 0)

    def test_p430_printed_counterexample_and_correct_side(self):
        pi = [1, 0, 2, 3, 4, 5, 6, 7]
        wrong = [core.parity(pi[z & 7] & (z >> 3)) ^ int((z >> 3) == 1) for z in range(64)]
        self.assertEqual(max(map(abs, direct_walsh(wrong))), 16)
        spec = core.construct_spec('mm', 6, pi=pi, g=[0, 1, 0, 0, 0, 0, 0, 0])
        self.assertEqual(set(map(abs, direct_walsh(spec['table']))), {8})

    def test_nonlinear_mm_and_odd_dimension_rejection(self):
        r = core.analyze(core.construct_spec('mm', 6, pi=[1, 0, 2, 3, 4, 5, 6, 7], g=[0, 1, 0, 1, 1, 0, 0, 1]))
        self.assertTrue(r['vectorial_bent'])
        with self.assertRaises(core.ResearchError):
            core.construct_spec('mm', 3)
        with self.assertRaises(core.ResearchError):
            core.construct_spec('mm', 4, pi=[0, 0, 2, 3])

    def test_autocorrelation_and_nearest_affine(self):
        rng = random.Random(71)
        for n in range(1, 6):
            t = [rng.randrange(2) for _ in range(1 << n)]
            c = core.analyze({'n': n, 'm': 1, 'table': t})['components'][0]
            self.assertEqual(c['autocorrelation'], direct_ac(t))
            distances = [sum(t[x] ^ ((a & x).bit_count() % 2) ^ b for x in range(1 << n))
                         for a in range(1 << n) for b in (0, 1)]
            self.assertEqual(c['nonlinearity'], min(distances))

    def test_random_ddt_code_and_all_components_against_direct_definitions(self):
        rng = random.Random(17)
        for n, m in [(2, 2), (3, 2), (4, 3)]:
            table = [rng.randrange(1 << m) for _ in range(1 << n)]
            r = core.analyze({'n': n, 'm': m, 'table': table}, include_ddt=True)
            for row in r['ddt_nonzero_direction_rows']:
                u = row['direction']
                self.assertEqual(row['counts'], [sum(table[x ^ u] ^ table[x] == v for x in range(1 << n)) for v in range(1 << m)])
            for c in r['components']:
                self.assertEqual(c['walsh'], direct_walsh([(c['mask'] & y).bit_count() % 2 for y in table]))
            words = {tuple(((a & x).bit_count() + (b & table[x]).bit_count() + c) % 2 for x in range(1 << n))
                     for a in range(1 << n) for b in range(1 << m) for c in (0, 1)}
            self.assertEqual(r['generated_code']['weight_distribution'], dict(Counter(map(sum, words))))

    def test_zero_and_nonzero_constant_conventions(self):
        for value, degree in [(0, -1), (1, 0)]:
            r = core.analyze({'n': 3, 'm': 1, 'table': [value] * 8}, advanced=True)
            c = r['components'][0]
            self.assertEqual(c['degree'], degree)
            self.assertEqual(c['correlation_immunity_order'], 3)
            self.assertIsNone(c['resiliency_order'])
            self.assertEqual(c['algebraic_immunity']['value'], 0)
            self.assertEqual(c['quadratic_polar']['rank'], 0)

    def test_parity_resiliency(self):
        t = [x.bit_count() % 2 for x in range(16)]
        c = core.analyze({'n': 4, 'm': 1, 'table': t})['components'][0]
        self.assertEqual(c['resiliency_order'], 3)
        self.assertEqual(c['correlation_immunity_order'], 3)

    def test_exact_ai_against_all_n3_functions(self):
        for encoded in range(256):
            t = [(encoded >> x) & 1 for x in range(8)]
            result = core.algebraic_immunity(t)
            self.assertEqual(result['value'], direct_ai(t))
            g = evaluate_anf(result['witness_anf_monomial_masks'], 3)
            self.assertEqual(result['witness_table'], g)
            self.assertTrue(any(g))
            side = result['annihilates'] == 'f+1'
            self.assertTrue(all(not ((t[x] ^ side) & g[x]) for x in range(8)))

    def test_nl2_exhaustive_truth_table_oracle(self):
        t = [int(x == 7) for x in range(8)]
        r = core.second_order_nonlinearity(t)
        # RM(2,3) is exactly the set of even-weight truth tables.
        expected = min(sum(a != b for a, b in zip(t, bits)) for bits in itertools.product((0, 1), repeat=8) if sum(bits) % 2 == 0)
        self.assertEqual(r['value'], expected)
        self.assertEqual(r['value'], sum(a != b for a, b in zip(t, r['nearest_table'])))
        self.assertEqual(evaluate_anf(r['nearest_anf_monomial_masks'], 3), r['nearest_table'])

    def test_cubic_not_quadratic(self):
        t = [int((x & 7) == 7) for x in range(16)]
        r = core.analyze({'n': 4, 'm': 1, 'table': t})
        self.assertEqual(r['degree'], 3)
        self.assertEqual(r['components'][0]['quadratic_polar']['status'], 'not_applicable')
        self.assertEqual(r['quadratic_derivatives']['status'], 'not_applicable')

    def test_gold_even_vs_odd(self):
        for n in (2, 3, 4, 5):
            r = core.analyze(core.construct_spec('gold', n))
            self.assertEqual(r['differential_uniformity'], 2)
            self.assertEqual(r['permutation'], bool(n % 2))
        for params in ({'n': 4, 'k': 2}, {'n': 3, 'polynomial': 0b1111}):
            with self.assertRaises(core.ResearchError):
                core.construct_spec('gold', **params)

    def test_budgeted_advanced_skip_and_code_skip(self):
        spec = {'n': 9, 'm': 1, 'table': [x.bit_count() % 2 for x in range(512)]}
        r = core.analyze(spec, max_n=9, advanced=True)
        self.assertEqual(r['components'][0]['algebraic_immunity']['status'], 'not_computed')
        self.assertEqual(r['components'][0]['second_order_nonlinearity']['status'], 'not_computed')
        self.assertEqual(r['generated_code']['enumeration_status'], 'not_computed')
        self.assertIsNone(r['generated_code']['minimum_positive_weight'])

    def test_ai_n6_witness_and_limits(self):
        t = core.construct_spec('mm', 6, g=[0, 0, 0, 0, 0, 0, 0, 1])['table']
        a = core.algebraic_immunity(t)
        self.assertEqual(a['status'], 'exact')
        self.assertTrue(1 <= a['value'] <= 3)
        g = evaluate_anf(a['witness_anf_monomial_masks'], 6)
        self.assertEqual(g, a['witness_table'])
        self.assertTrue(any(g))
        side = a['annihilates'] == 'f+1'
        self.assertTrue(all(not ((t[x] ^ side) & g[x]) for x in range(64)))


class InputAndCliTests(unittest.TestCase):
    def test_invalid_inputs(self):
        bad = [None, [], {}, {'n': True, 'm': 1, 'table': [0, 1]},
               {'n': 0, 'm': 1, 'table': [0]}, {'n': 1, 'm': 2, 'table': [0, 1]},
               {'n': 2, 'm': 1, 'table': [0]}, {'n': 1, 'm': 1, 'table': [0, True]},
               {'n': 1, 'm': 1, 'table': [0, 2]}, {'n': 1, 'm': 1, 'table': [-1, 0]},
               {'n': 1, 'm': 1, 'table': [0.0, 1]}]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(core.ResearchError):
                core.analyze(value)

    def test_budget_rejection(self):
        with self.assertRaises(core.ResearchError):
            core.analyze({'n': 9, 'm': 1, 'table': [0] * 512})
        with self.assertRaises(core.ResearchError):
            core.analyze(core.demo_spec('scalar-bent'), max_work=1)
        with self.assertRaises(core.ResearchError):
            core.analyze({'n': 12, 'm': 12, 'table': [0] * 4096}, max_n=12, max_work=1_000_000_000)

    def test_cli_roundtrip_and_failure_no_output(self):
        script = Path(core.__file__).resolve()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output = root / 'result.json'
            proc = subprocess.run([sys.executable, str(script), 'demo', '--case', 'apn-cube', '--out', str(output), '--advanced'], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(result['differential_uniformity'], 2)
            spec = root / 'spec.json'
            spec.write_text(json.dumps(result['input']), encoding='utf-8')
            replay = root / 'replay.json'
            proc = subprocess.run([sys.executable, str(script), 'analyze', '--input', str(spec), '--out', str(replay)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(replay.read_text())['truth_table_sha256'], result['truth_table_sha256'])
            bad = root / 'bad.json'
            bad.write_text('{"n":false}', encoding='utf-8')
            badout = root / 'never-created.json'
            proc = subprocess.run([sys.executable, str(script), 'analyze', '--input', str(bad), '--out', str(badout)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(badout.exists())
            self.assertIn('error:', proc.stderr)

    def test_constructor_cli(self):
        script = Path(core.__file__).resolve()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            params = root / 'params.json'
            params.write_text(json.dumps({'pi': [1, 0, 2, 3], 'g': [0, 1, 1, 1]}))
            output = root / 'constructed.json'
            proc = subprocess.run([sys.executable, str(script), 'construct', '--family', 'mm', '--n', '4', '--params', str(params), '--out', str(output)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(output.read_text())['vectorial_bent'])
            proc = subprocess.run([sys.executable, str(script), 'construct', '--family', 'gold', '--n', '3', '--params', str(params), '--out', str(root / 'invalid.json')], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse((root / 'invalid.json').exists())

    def test_cli_preserves_input_and_parameters(self):
        script = Path(core.__file__).resolve()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'input.json'
            original = json.dumps({'n':2,'m':1,'table':[0,0,0,1]})
            path.write_text(original, encoding='utf-8')
            proc = subprocess.run([sys.executable,str(script),'analyze','--input',str(path),'--out',str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode,2)
            self.assertEqual(path.read_text(encoding='utf-8'),original)
            params = json.dumps({'pi':[0,1],'g':[0,0]})
            path.write_text(params, encoding='utf-8')
            proc = subprocess.run([sys.executable,str(script),'construct','--family','mm','--n','2','--params',str(path),'--out',str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode,2)
            self.assertEqual(path.read_text(encoding='utf-8'),params)


if __name__ == '__main__':
    unittest.main(verbosity=2)
