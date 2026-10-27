import itertools
import unittest
from research_extensions import ea, macwilliams, oa, design, sequence
from search_monomials import search


class ExtensionsTests(unittest.TestCase):
    def test_ea_identity(self):
        self.assertTrue(ea(dict(n=2, m=2, table=[0,1,3,2], target=[0,1,3,2]))['matches_target'])

    def test_ea_affine_changes_permutation(self):
        result = ea(dict(n=2, m=2, table=[0,1,2,3], affine_rows=[1,2]))
        self.assertEqual(result['table'], [0]*4)

    def test_ea_noninvertible(self):
        with self.assertRaises(ValueError):
            ea(dict(n=2, m=1, table=[0,0,0,1], input_rows=[1,1]))

    def test_ea_boolean_rejected(self):
        with self.assertRaises(ValueError):
            ea(dict(n=1, m=1, table=[False,1]))

    def test_macwilliams_even3(self):
        result = macwilliams(dict(length=3, distribution={'0':1,'2':3}))
        self.assertTrue(result['nonnegative_integers'])
        self.assertEqual(result['transform'], {'0':1,'3':1})

    def test_macwilliams_invalid_candidate(self):
        self.assertFalse(macwilliams(dict(length=3, distribution={'0':1,'1':3}))['nonnegative_integers'])

    def test_macwilliams_size(self):
        with self.assertRaises(ValueError):
            macwilliams(dict(length=3, distribution={'0':1,'2':2}))

    def test_oa_full(self):
        rows = [list(x) for x in itertools.product((0,1), repeat=3)]
        self.assertTrue(oa(dict(rows=rows, strength=3))['is_orthogonal_array'])

    def test_oa_failure_witness(self):
        self.assertFalse(oa(dict(rows=[[0,0],[0,1]], strength=1))['is_orthogonal_array'])

    def test_oa_strength0(self):
        self.assertEqual(oa(dict(rows=[[1,0]], strength=0))['index'], 1)

    def test_design_complete(self):
        blocks = list(map(list, itertools.combinations(range(4), 2)))
        result = design(dict(v=4, k=2, t=1, blocks=blocks))
        self.assertTrue(result['is_design'])
        self.assertEqual(result['lambda_value'], 3)

    def test_design_failure(self):
        self.assertFalse(design(dict(v=4, k=2, t=1, blocks=[[0,1],[0,2]]))['is_design'])

    def test_design_duplicate(self):
        with self.assertRaises(ValueError):
            design(dict(v=4, k=2, t=1, blocks=[[0,1],[1,0]]))

    def test_sequence_groups_differ(self):
        spec = dict(sequence=[0,0,0,0,0,0,1,1])
        self.assertNotEqual(sequence(dict(spec, shift_group='cyclic'))['correlation'],
                            sequence(dict(spec, shift_group='xor'))['correlation'])

    def test_sequence_xor_badlength(self):
        with self.assertRaises(ValueError):
            sequence(dict(sequence=[0,1,0], shift_group='xor'))

    def test_sequence_group_required(self):
        with self.assertRaises(ValueError):
            sequence(dict(sequence=[0,1]))

    def test_search_GF8_APN_permutations(self):
        result = search(dict(n=3, polynomial=11, exponents=[1,3,5],
                             filters=dict(max_delta=2, require_permutation=True)))
        self.assertEqual(result['accepted_exponents'], [3,5])
        self.assertEqual(result['candidates'][0]['differential_uniformity'], 8)
        self.assertEqual(result['novelty'], 'not_evaluated')

    def test_search_reducible_polynomial(self):
        with self.assertRaises(ValueError):
            search(dict(n=3, polynomial=15, exponents=[3]))

    def test_search_unknown_filter(self):
        with self.assertRaises(ValueError):
            search(dict(n=3, polynomial=11, exponents=[3], filters=dict(unknown=4)))

    def test_search_invalid_exponent(self):
        with self.assertRaises(ValueError):
            search(dict(n=3, polynomial=11, exponents=[True]))


if __name__ == '__main__':
    unittest.main()
