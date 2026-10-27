import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import field_functions as field


def multiply_oracle(a,b,p):
    # Unreduced polynomial product then long division, independently of shifts in gf_mul.
    raw=0
    for i in range(b.bit_length()):
        if b >> i & 1:
            raw ^= a << i
    while raw.bit_length() >= p.bit_length():
        raw ^= p << (raw.bit_length()-p.bit_length())
    return raw


def power_oracle(a,e,p):
    result=1
    for _ in range(e):
        result=multiply_oracle(result,a,p)
    return result


def trace_oracle(a,n,p):
    result=0
    for i in range(n):
        result ^= power_oracle(a,1 << i,p)
    return result


class FieldTests(unittest.TestCase):
    def test_multiplication_GF4_GF8(self):
        for n,p in [(2,7),(3,11)]:
            for a,b in itertools.product(range(1 << n),repeat=2):
                self.assertEqual(field.gf_mul(a,b,p),multiply_oracle(a,b,p))

    def test_polynomial_direct_oracle(self):
        for n,p in [(2,7),(3,11)]:
            terms=[dict(coefficient=3,exponent=5),dict(coefficient=1,exponent=0),dict(coefficient=2,exponent=3)]
            result=field.polynomial_table(dict(n=n,polynomial=p,terms=terms))
            expected=[]
            for x in range(1 << n):
                y=0
                for term in terms:
                    y ^= multiply_oracle(term['coefficient'],power_oracle(x,term['exponent'],p),p)
                expected.append(y)
            self.assertEqual(result['table'],expected)

    def test_zero_exponent_at_zero(self):
        result=field.polynomial_table(dict(n=3,polynomial=11,terms=[dict(coefficient=5,exponent=0)]))
        self.assertEqual(result['table'],[5]*8)

    def test_empty_and_cancelled_terms(self):
        spec=dict(n=3,polynomial=11,terms=[])
        self.assertEqual(field.polynomial_table(spec)['table'],[0]*8)
        terms=[dict(coefficient=3,exponent=0)]*2
        self.assertEqual(field.polynomial_table(dict(spec,terms=terms))['table'],[0]*8)

    def test_trace_direct_linearity(self):
        for n,p in [(1,3),(2,7),(3,11),(4,19)]:
            values=[field.absolute_trace(x,n,p) for x in range(1 << n)]
            self.assertEqual(values,[trace_oracle(x,n,p) for x in range(1 << n)])
            self.assertEqual(values.count(1),1 << (n-1))
            for a,b in itertools.product(range(1 << n),repeat=2):
                self.assertEqual(values[a^b],values[a]^values[b])

    def test_trace_one_even_not_zero_map(self):
        values=[field.absolute_trace(x,2,7) for x in range(4)]
        self.assertEqual(values[1],0)
        self.assertIn(1,values)

    def test_trace_polynomial_table(self):
        spec=dict(n=3,polynomial=11,terms=[dict(coefficient=3,exponent=3),dict(coefficient=1,exponent=0)])
        vector=field.polynomial_table(spec)
        scalar=field.polynomial_table(spec,trace=True)
        self.assertEqual(scalar['m'],1)
        self.assertEqual(scalar['table'],[trace_oracle(y,3,11) for y in vector['table']])

    def test_dual_basis_all_GF4_ordered_bases(self):
        for b in itertools.permutations(range(1,4),2):
            result=field.dual_basis(dict(n=2,polynomial=7,basis=list(b)))
            expected=[next(d for d in range(4) if all(trace_oracle(multiply_oracle(bi,d,7),2,7)==int(i==j) for i,bi in enumerate(b))) for j in range(2)]
            self.assertEqual(result['dual_basis'],expected)

    def test_dual_basis_GF8_arbitrary(self):
        spec=dict(n=3,polynomial=11,basis=[3,5,7])
        result=field.dual_basis(spec)
        self.assertEqual(result['pairing_matrix'],[[1,0,0],[0,1,0],[0,0,1]])
        for x,c in enumerate(result['standard_to_basis_coordinates']):
            expected=next(c for c in range(8) if self.reconstruct(c,spec['basis'])==x)
            self.assertEqual(c,expected)

    @staticmethod
    def reconstruct(c,basis):
        value=0
        for i,b in enumerate(basis):
            if c >> i & 1:value ^= b
        return value

    def test_coordinate_functions_as_traces(self):
        for n,p in [(2,7),(3,11),(4,19)]:
            dual=field.dual_basis(dict(n=n,polynomial=p))['dual_basis']
            for i,d in enumerate(dual):
                scalar=field.polynomial_table(dict(n=n,polynomial=p,terms=[dict(coefficient=d,exponent=1)]),trace=True)
                self.assertEqual(scalar['table'],[(x >> i)&1 for x in range(1 << n)])

    def test_basis_rejected_for_construction(self):
        with self.assertRaises(field.FieldError):
            field.polynomial_table(dict(n=2,polynomial=7,terms=[],basis=[1,2]))

    def test_reducible_wrong_degree(self):
        for p in [9,15,7,19]:
            with self.assertRaises(field.FieldError):
                field.polynomial_table(dict(n=3,polynomial=p,terms=[]))

    def test_dependent_basis(self):
        for basis in [[1,2,3],[1,1,4],[0,1,2], [1,2]]:
            with self.assertRaises(field.FieldError):
                field.dual_basis(dict(n=3,polynomial=11,basis=basis))

    def test_invalid_integer_types(self):
        for spec in [dict(n=True,polynomial=11,terms=[]),dict(n=3,polynomial=11.0,terms=[]),dict(n=3,polynomial=11,terms=[dict(coefficient=True,exponent=1)]),dict(n=3,polynomial=11,terms=[dict(coefficient=1,exponent=1.0)])]:
            with self.assertRaises(field.FieldError):field.polynomial_table(spec)

    def test_limits_terms_exponents_coefficients(self):
        for terms in [[dict(coefficient=8,exponent=1)],[dict(coefficient=1,exponent=-1)],[dict(coefficient=1,exponent=(1 << 20)+1)],[dict(coefficient=1,exponent=1)]*65,[dict(coefficient=1,exponent=1,extra=1)]]:
            with self.assertRaises(field.FieldError):field.polynomial_table(dict(n=3,polynomial=11,terms=terms))
        with self.assertRaises(field.FieldError):field.polynomial_table(dict(n=9,polynomial=0x211,terms=[]))

    def test_budget(self):
        with self.assertRaises(field.FieldError):
            field.polynomial_table(dict(n=3,polynomial=11,terms=[dict(coefficient=1,exponent=3)]),max_work=1)
        with self.assertRaises(field.FieldError):field.dual_basis(dict(n=3,polynomial=11),max_work=1)

    def test_cli_success_and_analysis_replay(self):
        script=Path(field.__file__).resolve()
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); inp=d/'input.json';out=d/'field.json'
            inp.write_text(json.dumps(dict(n=3,polynomial=11,terms=[dict(coefficient=1,exponent=3)])),encoding='utf-8')
            proc=subprocess.run([sys.executable,str(script),'polynomial','--input',str(inp),'--out',str(out)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            result=json.loads(out.read_text(encoding='utf-8'))
            import research_core
            analysis=research_core.analyze({k:result[k] for k in ['n','m','table']})
            self.assertEqual(analysis['differential_uniformity'],2)
            self.assertTrue(analysis['permutation'])

    def test_cli_rejects_overwrite_and_no_failure_output(self):
        script=Path(field.__file__).resolve()
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);inp=d/'input.json';out=d/'result.json'
            original=json.dumps(dict(n=3,polynomial=11,terms=[]))
            inp.write_text(original,encoding='utf-8')
            proc=subprocess.run([sys.executable,str(script),'trace','--input',str(inp),'--out',str(inp)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2)
            self.assertEqual(inp.read_text(encoding='utf-8'),original)
            inp.write_text('{"n":false}',encoding='utf-8')
            proc=subprocess.run([sys.executable,str(script),'dual-basis','--input',str(inp),'--out',str(out)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2)
            self.assertFalse(out.exists())


if __name__=='__main__':unittest.main(verbosity=2)
