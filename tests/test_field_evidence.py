"""Located-field bookkeeping controls, not a semantic-reading validator."""
import copy
import csv
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_audit import field_evidence_summary

def rows(name):
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))

class LocatedFieldControls(unittest.TestCase):
    def setUp(self):
        self.evidence = rows('field_evidence.csv')
        self.extractions = rows('study_extractions.csv')
        self.locations = rows('source_locations.csv')
        self.readings = rows('source_readings.csv')

    def summary(self, evidence=None, locations=None):
        return field_evidence_summary(self.evidence if evidence is None else evidence,
                                     self.extractions, self.locations if locations is None else locations,
                                     self.readings if evidence != [] else [])

    def test_exact_denominators_without_semantic_promotion(self):
        self.assertEqual(self.summary(), dict(located_field_rows=588, located_recoded_records=84,
                         total_coding_fields=679, records_without_supplementary_field_bindings=13,
                         semantic_interpretation_verified_by_code=False))

    def test_empty_supplement_is_zero_not_all_inherited_readings(self):
        self.assertEqual(self.summary([])['located_recoded_records'], 0)

    def test_representation_label_cannot_claim_completed_reading(self):
        changed = copy.deepcopy(self.readings)
        changed[0]['reading_scope'] = 'complete_retrieved_pdf'
        with self.assertRaisesRegex(ValueError, 'representation boundary'):
            field_evidence_summary(self.evidence, self.extractions, self.locations, changed)

    def test_duplicate_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.summary(self.evidence + [copy.deepcopy(self.evidence[0])])

    def test_missing_field_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.summary(self.evidence[1:])

    def test_changed_interpretation_requires_rebinding(self):
        changed = copy.deepcopy(self.evidence)
        changed[0]['coded_value'] += ' another interpretation'
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.summary(changed)

    def test_other_source_and_metadata_only_locators_are_rejected(self):
        for field, value in [('source_location', 'DOI record only'),
                             ('fulltext_url', 'https://example.org/owned-other.pdf')]:
            changed = copy.deepcopy(self.evidence)
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'bound scoped fulltext'):
                self.summary(changed)

    def test_selected_reading_cannot_become_complete_recoding(self):
        changed = copy.deepcopy(self.locations)
        next(r for r in changed if r['bib_key'] == 'repack')['content_check_status'] = 'selected_fulltext_checked'
        with self.assertRaisesRegex(ValueError, 'bound scoped fulltext'):
            self.summary(locations=changed)

    def test_nonexistent_pdf_page_cannot_be_a_field_binding(self):
        changed = copy.deepcopy(self.evidence)
        changed[0]['source_location'] = 'Author PDF pp. 9999: Section 2.2/Table 2'
        with self.assertRaisesRegex(ValueError, 'outside retrieved PDF'):
            self.summary(changed)

    def test_version_change_requires_all_field_bindings_to_be_updated(self):
        changed = copy.deepcopy(self.evidence)
        changed[0]['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'exact source version'):
            self.summary(changed)

    def test_zero_reversed_and_out_of_bounds_ranges_are_rejected(self):
        for pages in ('0', '3-2', '1-9999'):
            changed = copy.deepcopy(self.evidence)
            changed[0]['source_location'] = 'Author PDF pp. ' + pages + ': Section 2'
            with self.subTest(pages=pages), self.assertRaisesRegex(ValueError, 'outside retrieved PDF'):
                self.summary(changed)

if __name__ == '__main__':
    unittest.main()
