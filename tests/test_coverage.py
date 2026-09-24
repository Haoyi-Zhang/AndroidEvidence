"""Independent completion oracle plus benign negative controls (stdlib only)."""
from __future__ import annotations
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from coverage import summarize, minimal_known_cover


def oracle(matrix):
    # Deliberately does not call boolean_coverage, status, or validate.
    rows, cols = len(matrix),len(matrix[0])
    flat = [x for row in matrix for x in row]
    positions = [i for i,x in enumerate(flat) if x is None]
    d_results, m_results = set(), set()
    completions = 0
    for assignment in product((0,1),repeat=len(positions)):
        complete = list(flat)
        for pos,bit in zip(positions,assignment): complete[pos]=bit
        full_rows = 0
        for r in range(rows):
            total = sum(complete[r*cols+c] for c in range(cols))
            if total == cols: full_rows += 1
        covered_cols=0
        for c in range(cols):
            total=sum(complete[r*cols+c] for r in range(rows))
            if total>0: covered_cols+=1
        d_results.add(full_rows>0);m_results.add(covered_cols==cols)
        completions+=1
    def label(values):
        return 'covered' if values == {True} else ('gap' if values == {False} else 'undetermined')
    return label(d_results),label(m_results),completions


def exhaustive_3x3():
    checked=0; completions=0
    for flat in product((0,1,None),repeat=9):
        matrix=[list(flat[r*3:(r+1)*3]) for r in range(3)]
        expected_d,expected_m,count=oracle(matrix)
        got=summarize(matrix)
        if (got['direct'],got['mosaic']) != (expected_d,expected_m):
            raise AssertionError((matrix,got,expected_d,expected_m))
        checked+=1;completions+=count
    if checked != 19683 or completions != 262144:
        raise AssertionError('exhaustive accounting changed')
    return {'ternary_matrices':checked,'binary_completions_across_matrices':completions,
            'mismatches':0,'domain':'exactly 3 rows by 3 columns; all ternary matrices'}


class Controls(unittest.TestCase):
    def test_complete_review_negative_control(self):
        s=summarize([[1,1,1],[None,None,None]])
        self.assertEqual((s['direct'],s['mosaic']),('covered','covered'))
    def test_disjoint_mosaic(self):
        s=summarize([[1,0,0],[0,1,0],[0,0,1]])
        self.assertEqual((s['direct'],s['mosaic']),('gap','covered'))
    def test_unknown_is_not_absent(self):
        self.assertEqual(summarize([[None]])['mosaic'],'undetermined')
        self.assertEqual(summarize([[0]])['mosaic'],'gap')
    def test_partial_matrix_not_full_gap(self):
        self.assertEqual(summarize([[1,None],[None,1]])['direct'],'undetermined')
    def test_minimal_cover(self):
        self.assertEqual(minimal_known_cover([[1,0],[0,1],[1,1]]),[2])
    def test_invalid(self):
        for matrix in ([],[[]],[[1],[1,0]],[[2]],[[True]],[[1.0]], [['1']],[[1]*33]):
            with self.assertRaises(ValueError):summarize(matrix)
    def test_exhaustive_all_3x3(self):
        self.assertEqual(exhaustive_3x3()['mismatches'],0)

if __name__ == '__main__': unittest.main(verbosity=2)
