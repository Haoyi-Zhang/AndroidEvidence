"""Reader-declaration identity controls; these never certify source understanding."""
from copy import deepcopy
import csv
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_audit import semantic_reading_summary


def read(name):
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


class SemanticReadingBindings(unittest.TestCase):
    def setUp(self):
        self.rows = read('semantic_readings.csv')
        self.extractions = read('study_extractions.csv')
        self.sources = read('source_readings.csv')

    def check(self, rows=None):
        return semantic_reading_summary(self.rows if rows is None else rows, self.extractions, self.sources)

    def test_current_assessments_cover_acquired_not_all_corpus_sources(self):
        result = self.check()
        self.assertEqual(result['declared_complete_seven_field_codings'], len(self.rows))
        self.assertEqual(result['acquired_records_without_complete_coding'], len(self.sources) - len(self.rows))
        self.assertEqual(result['acquired_records_without_complete_coding'], 0)
        self.assertLess(len(self.rows), len(self.extractions))
        self.assertIs(result['semantic_interpretation_verified_by_code'], False)
        self.assertIs(result['independent_second_coder'], False)

    def test_partial_assessments_remain_partial_without_promotion(self):
        partial = self.rows[:-1]
        result = self.check(partial)
        self.assertEqual(result['declared_complete_seven_field_codings'], len(partial))
        self.assertEqual(result['acquired_records_without_complete_coding'], 1)
        self.assertIs(result['semantic_interpretation_verified_by_code'], False)
        self.assertIs(result['independent_second_coder'], False)

    def test_empty_reader_declaration_does_not_adopt_legacy_labels(self):
        self.assertEqual(self.check([])['declared_complete_seven_field_codings'], 0)

    def test_duplicate_or_unknown_assessment_rejected(self):
        for rows in (self.rows + [deepcopy(self.rows[0])], [{**self.rows[0], 'bib_key': 'owned-absent'}]):
            with self.subTest(rows=rows[-1]['bib_key']), self.assertRaisesRegex(ValueError, 'duplicate or unbound'):
                self.check(rows)

    def test_source_or_field_change_requires_reassessment(self):
        for field in ('source_sha256', 'fields_sha256'):
            changed = deepcopy(self.rows)
            changed[0][field] = '0' * 64
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'stale'):
                self.check(changed)

    def test_changed_coded_value_cannot_reuse_assessment(self):
        changed = deepcopy(self.extractions)
        next(r for r in changed if r['bib_key'] == self.rows[0]['bib_key'])['observation'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'stale'):
            semantic_reading_summary(self.rows, changed, self.sources)

    def test_partial_date_or_independence_promotion_rejected(self):
        for field, value in (('reading_extent', 'abstract_only'), ('assessment_date', '1900-01-01'),
                             ('independent', 'true')):
            changed = deepcopy(self.rows)
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'boundary'):
                self.check(changed)


if __name__ == '__main__':
    unittest.main()
