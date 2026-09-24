from pathlib import Path
import csv,json,sys,tempfile,shutil,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import audit

class LedgerControls(unittest.TestCase):
    def test_withdrawn_sbom_and_boundary_exclusion(self):
        result=audit.compute()
        self.assertNotIn('R07',result['analyses']['base_all']['record_ids'])
        self.assertNotIn('R10',result['analyses']['base_all']['record_ids'])
        self.assertNotIn('R11',result['analyses']['base_all']['record_ids'])
    def test_no_gap_promotion(self):
        result=audit.compute()
        self.assertEqual(result['analyses']['base_all']['mosaic'],'undetermined')
        self.assertFalse(result['scientific_lock'])
    def test_recheck_correction_and_fraction(self):
        result=audit.compute()
        self.assertEqual(result['recheck']['completed_cells'],21)
        self.assertGreaterEqual(result['recheck']['fraction'],0.15)
        self.assertEqual(result['analyses']['publication_documented_coarse']['mosaic'],'covered')
    def mutate_and_check(self,filename,mutate):
        with tempfile.TemporaryDirectory(prefix='mobile-ledger-') as d:
            p=Path(d);shutil.copytree(audit.ROOT/'data',p/'data')
            path=p/'data'/filename
            with path.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
            mutate(rows)
            with path.open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            with patch.object(audit,'ROOT',p):
                with self.assertRaises(ValueError):audit.load_data()
    def test_unverified_primary_rejected(self):
        def change(rows):
            for r in rows:
                if r['record_id']=='P02':r['main_corpus_included']='true'
        self.mutate_and_check('records.csv',change)
    def test_unknown_to_absence_without_reading_rejected(self):
        def change(rows):
            r=next(r for r in rows if r['record_id']=='R05')
            r['value']='0';r['basis']='complete_scope_absence'
        self.mutate_and_check('coverage.csv',change)
    def test_abstract_positive_rejected(self):
        def change(rows):
            r=next(r for r in rows if r['record_id']=='R05')
            r['value']='1';r['basis']='body_positive';r['source_location']='Abstract'
        self.mutate_and_check('coverage.csv',change)
    def test_completed_rechecks_cannot_disappear(self):
        with tempfile.TemporaryDirectory(prefix='mobile-ledger-') as d:
            p=Path(d);shutil.copytree(audit.ROOT/'data',p/'data')
            (p/'data/rechecks.csv').unlink()
            with patch.object(audit,'ROOT',p):
                with self.assertRaises(ValueError):audit.compute()
    def test_duplicate_record_rejected(self):
        self.mutate_and_check('records.csv',lambda rows:rows.append(dict(rows[0])))
    def test_duplicate_cell_rejected(self):
        self.mutate_and_check('coverage.csv',lambda rows:rows.append(dict(rows[0])))

if __name__=='__main__':unittest.main(verbosity=2)
