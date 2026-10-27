import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
import sbox_criteria as sbox
import graph_equivalence as graph
from research_core import ResearchError, construct_spec, parity, gf2_basis


class SboxTests(unittest.TestCase):
    def test_all_two_bit_permutations_bct_pair_equations(self):
        for t in itertools.permutations(range(4)):
            report=sbox.analyze(dict(n=2,m=2,table=list(t)),True)
            for row in report['bct']['nonzero_row_table']:
                a=row['input_difference']
                for b in range(1,4):
                    # Independent pair-equation definition, no inverse lookup.
                    count=sum(t[x]^t[y]==b and t[x^a]^t[y^a]==b for x in range(4) for y in range(4))
                    self.assertEqual(row['counts'][b],count)

    def test_dlct_against_direct_count_and_autocorrelation(self):
        rng=random.Random(20261027)
        for _ in range(20):
            t=[rng.randrange(4) for _ in range(8)]
            r=sbox.analyze(dict(n=3,m=2,table=t),True)
            for row in r['dlct']['nonzero_direction_rows']:
                u=row['direction']
                for b,v in enumerate(row['count_bias']):
                    equal=sum(parity(b&(t[x]^t[x^u]))==0 for x in range(8))
                    self.assertEqual(v,equal-4)
                    self.assertEqual(2*v,sum((-1)**parity(b&(t[x]^t[x^u])) for x in range(8)))

    def test_nonpermutation_continues_dlct(self):
        r=sbox.analyze(dict(n=2,m=2,table=[0]*4))
        self.assertEqual(r['bct']['status'],'not_applicable')
        self.assertEqual(r['dlct']['maximum_absolute_nontrivial_entry'],2)

    def test_coordinate_sac_strictly_weaker_than_all_components(self):
        q=[((x&1)*((x>>1)&1))^(((x>>2)&1)*((x>>3)&1)) for x in range(16)]
        t=[q[x]|((q[x]^(x&1))<<1) for x in range(16)]
        r=sbox.analyze(dict(n=4,m=2,table=t))
        self.assertTrue(r['coordinate_sac']['satisfied'])
        self.assertEqual(r['all_component_pc']['order'],0)

    def test_vector_bent_pc_all_directions(self):
        from research_core import demo_spec
        self.assertEqual(sbox.analyze(demo_spec('vector-bent'))['all_component_pc']['order'],4)

    def test_identity_and_cube(self):
        r=sbox.analyze(dict(n=3,m=3,table=list(range(8))))
        self.assertEqual(r['bct']['boomerang_uniformity'],8)
        self.assertFalse(r['coordinate_sac']['satisfied'])
        c=sbox.analyze(construct_spec('gold',3,polynomial=11))
        self.assertEqual(c['bct']['boomerang_uniformity'],2)

    def test_budgets_and_bad_types(self):
        with self.assertRaises(ResearchError):sbox.analyze(dict(n=3,m=3,table=list(range(8))),max_work=1)
        with self.assertRaises(ResearchError):sbox.analyze(dict(n=True,m=1,table=[0,1]))
        with self.assertRaises(ResearchError):sbox.analyze(dict(n=1,m=1,table=[False,1]))


class GraphTests(unittest.TestCase):
    def test_identity_certificate(self):
        s=dict(n=2,m=1,table=[0,0,0,1],graph_rows=[1,2,4],target=[0,0,0,1])
        self.assertTrue(graph.certificate(s)['matches_target'])

    def test_inverse_by_graph_swap(self):
        t=construct_spec('gold',3,polynomial=11)['table']
        r=graph.certificate(dict(n=3,m=3,table=t,graph_rows=[8,16,32,1,2,4]))
        self.assertEqual([r['table'][t[x]] for x in range(8)],list(range(8)))
        self.assertEqual(graph.prefilter(dict(n=3,m=3,left=t,right=r['table']))['status'],'inconclusive')

    def test_swap_nonpermutation_is_not_function(self):
        r=graph.certificate(dict(n=2,m=2,table=[0,0,0,0],graph_rows=[4,8,1,2]))
        self.assertEqual(r['status'],'not_function_graph')
        self.assertEqual(len(r['witness']['original_inputs']),2)

    def test_mismatch_and_singular(self):
        with self.assertRaises(ResearchError):graph.certificate(dict(n=2,m=2,table=list(range(4)),graph_rows=[1,2,4,8],shift=1))
        with self.assertRaises(ResearchError):graph.prefilter(dict(n=2,m=1,left=[0]*4,right=[0]*4,unexpected=True))
        r=graph.certificate(dict(n=2,m=1,table=[0,0,0,1],graph_rows=[1,2,4],target=[0,0,0,0]))
        self.assertFalse(r['matches_target']);self.assertEqual(r['first_mismatch']['input'],3)
        with self.assertRaises(ResearchError):graph.certificate(dict(n=2,m=1,table=[0,0,0,1],graph_rows=[1,1,4]))

    def test_prefilter_distinguishes_and_never_certifies_match(self):
        self.assertEqual(graph.prefilter(dict(n=2,m=1,left=[0]*4,right=[0,0,0,1]))['status'],'proven_not_ccz_equivalent')
        self.assertEqual(graph.prefilter(dict(n=2,m=1,left=[0]*4,right=[0]*4))['status'],'inconclusive')

    def test_random_graph_changes_preserve_prefilter(self):
        rng=random.Random(9234);t=[0,1,3,2];checked=0
        for _ in range(80):
            rows=[rng.randrange(16) for _ in range(4)]
            if len(gf2_basis(rows))!=4:continue
            result=graph.certificate(dict(n=2,m=2,table=t,graph_rows=rows,graph_shift=rng.randrange(16)))
            if result['status']=='not_function_graph':continue
            checked+=1
            self.assertEqual(graph.prefilter(dict(n=2,m=2,left=t,right=result['table']))['status'],'inconclusive')
        self.assertGreater(checked,1)

    def test_histogram_counts_and_budgets(self):
        r=graph.prefilter(dict(n=2,m=1,left=[0]*4,right=[0]*4))
        self.assertEqual(sum(r['left']['absolute_graph_walsh_histogram'].values()),7)
        self.assertEqual(sum(r['left']['ddt_nonzero_direction_histogram'].values()),6)
        with self.assertRaises(ResearchError):graph.prefilter(dict(n=2,m=1,left=[0]*4,right=[0]*4),1)
        with self.assertRaises(ResearchError):graph.certificate(dict(n=2,m=1,table=[0]*4,graph_rows=[1,2,4]),1)


class CliTests(unittest.TestCase):
    def test_cli_success_bad_input_and_overwrite(self):
        directory=Path(__file__).resolve().parent
        for script,operation,spec in [('sbox_criteria.py','analyze',dict(n=2,m=2,table=[0,1,3,2])),('graph_equivalence.py','certificate',dict(n=2,m=1,table=[0]*4,graph_rows=[1,2,4]))]:
            with tempfile.TemporaryDirectory() as d:
                source=Path(d)/'input.json';out=Path(d)/'output.json';text=json.dumps(spec);source.write_text(text)
                cmd=[sys.executable,str(directory/script),operation,'--input',str(source),'--out']
                result=subprocess.run(cmd+[str(out)],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                result=subprocess.run(cmd+[str(source)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2);self.assertEqual(source.read_text(),text)
                source.write_text('{"n":false}')
                bad=Path(d)/'never.json';result=subprocess.run(cmd+[str(bad)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2);self.assertFalse(bad.exists())


if __name__=='__main__':unittest.main()
