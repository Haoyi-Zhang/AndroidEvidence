"""Bindings for 16 declared matrix decisions, not a semantic-reading oracle.

The named fixture is intentional: a decision/page/source change requires review,
not a blanket rewrite of aggregate expectations. Existing generic audit functions
check the field and reader declarations. No PDF or network access occurs here.
"""
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_audit import (CODING_FIELDS, MATRIX_DIMS, field_evidence_summary,
                          review_coverage_status, semantic_reading_summary)


# Each tuple is (admitted code, physical PDF pages), in the existing dimension
# vocabulary. These 16 judgments reuse three already-complete reader assessments.
ADMITTED = {
    'tpl': {
        'source_sha256': '81b7e75348530e622ea4438bb74788de6509a26431511a368624d86029fe845b',
        'fields_sha256': '86461be03f844c68b6984687d82045f9aab93f2b92581befcc5350497c02b0a8',
        'fulltext_url': 'https://lilicoding.github.io/papers/zhan2021research.pdf',
        'pages': 32,
        'cells': {
            'supply_chain_provenance': ('0', '4-8,10-15,19-22,26-28'),
            'ai_mediated_workflow': ('0', '1-32'),
        },
    },
    'wohlin': {
        'source_sha256': 'b45773e4cb8fd006eb4df616418f696888cd35bf434ca183c7f1a62e797d5b76',
        'fields_sha256': 'c867292bb4d49fc9ab659465145c7c5996950117dbdb5a814eb6ae560c156d21',
        'fulltext_url': 'https://www.wohlin.eu/ease14.pdf',
        'pages': 10,
        'cells': dict(zip(MATRIX_DIMS, (
            ('0', '1-4'), ('0', '1-10'), ('0', '1-10'), ('0', '4-5,9'),
            ('0', '1-10'), ('0', '1-10'), ('P', '3,5,7-10'),
        ))),
    },
    'kitchenham': {
        'source_sha256': '5519f5dd015191588a0239dbf3c48892f5b61833a297110a38220028d2b2c792',
        'fields_sha256': 'eab15ddefe8daa3922f43f9460572de1c648f903e0114faf5053e466601a8ed1',
        'fulltext_url': 'https://www.inf.ufsc.br/~aldo.vw/kitchenham.pdf',
        'pages': 33,
        'cells': dict(zip(MATRIX_DIMS, (
            ('0', '5-10'), ('0', '1-33'), ('0', '14-15'), ('0', '9-10,15-24'),
            ('0', '1-33'), ('0', '1-33'), ('P', '21-25,30'),
        ))),
    },
}


def read_csv(name):
    with (ROOT / 'data' / name).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def supplied_data():
    return {name: read_csv(name + '.csv') for name in (
        'review_gap_matrix', 'source_readings', 'semantic_readings',
        'field_evidence', 'source_locations', 'study_extractions')}


def page_set(text, limit):
    """Parse physical ranges without mistaking section numbers for pages."""
    result = set()
    for part in text.split(','):
        match = re.fullmatch(r'\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?\s*', part)
        if match is None:
            raise ValueError('invalid physical page expression')
        start, end = int(match[1]), int(match[2] or match[1])
        if not 1 <= start <= end <= limit:
            raise ValueError('page outside complete retrieved representation')
        result.update(range(start, end + 1))
    return result


class ReviewMatrixAdmissions(unittest.TestCase):
    def one(self, data, table, key):
        rows = [row for row in data[table] if row['bib_key'] == key]
        self.assertEqual(1, len(rows), (table, key))
        return rows[0]

    def check_admissions(self, data):
        # Exercise the production identity/boundary checks, not a substitute
        # parser that accepts a merely present metadata or acquisition row.
        field_evidence_summary(data['field_evidence'], data['study_extractions'],
                               data['source_locations'], data['source_readings'])
        semantic_reading_summary(data['semantic_readings'], data['study_extractions'],
                                 data['source_readings'])
        for key, expected in ADMITTED.items():
            row = self.one(data, 'review_gap_matrix', key)
            source = self.one(data, 'source_readings', key)
            reading = self.one(data, 'semantic_readings', key)
            location = self.one(data, 'source_locations', key)
            self.assertEqual('complete_scope_checked', location['content_check_status'])
            self.assertEqual('retrieved_pdf_locator_binding', source['reading_scope'])
            self.assertEqual('complete_retrieved_pdf_and_seven_fields', reading['reading_extent'])
            self.assertEqual('false', reading['independent'])
            self.assertEqual(expected['source_sha256'], source['source_sha256'])
            self.assertEqual(source['source_sha256'], reading['source_sha256'])
            self.assertEqual(expected['fields_sha256'], reading['fields_sha256'])
            self.assertEqual(expected['fulltext_url'], source['fulltext_url'])
            self.assertEqual(source['fulltext_url'], location['fulltext_url'])
            self.assertEqual(expected['pages'], int(source['pdf_page_count']))
            full_scope = re.search(r'\bPDF pp\. 1-(\d+)\b', row['source_basis'])
            self.assertIsNotNone(full_scope, key)
            self.assertEqual(expected['pages'], int(full_scope[1]))
            fields = [r for r in data['field_evidence'] if r['bib_key'] == key]
            self.assertCountEqual(CODING_FIELDS, [r['field'] for r in fields])
            for dimension, (code, pages) in expected['cells'].items():
                self.assertEqual(code, row[dimension], (key, dimension))
                locator = re.search(
                    r'(?:^|;\s+)' + re.escape(dimension)
                    + r':\s+PDF pp?\.\s*([0-9 ,\-\u2013]+):', row['source_basis'])
                self.assertIsNotNone(locator, (key, dimension))
                self.assertEqual(page_set(pages, expected['pages']),
                                 page_set(locator[1], expected['pages']), (key, dimension))

    def test_admitted_values_pages_and_existing_complete_assessments(self):
        self.assertEqual(16, sum(len(r['cells']) for r in ADMITTED.values()))
        self.check_admissions(supplied_data())

    def test_remaining_unknowns_and_protocol_derive_from_actual_matrix(self):
        data = supplied_data()
        expected = {key: set(MATRIX_DIMS) for key in
                    ('brereton', 'sufatrio', 'ohmstuke', 'reichert2024')}
        expected['wurepack2026'] = {'supply_chain_provenance',
                                   'authorization_policy', 'ai_mediated_workflow'}
        unknown = {r['bib_key']: {d for d in MATRIX_DIMS if r[d] == '?'}
                   for r in data['review_gap_matrix'] if any(r[d] == '?' for d in MATRIX_DIMS)}
        self.assertEqual(expected, unknown)
        counts = Counter(r[d] for r in data['review_gap_matrix'] for d in MATRIX_DIMS)
        protocol = json.loads((ROOT / 'data/protocol.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(map(len, expected.values())), counts['?'])
        self.assertEqual(counts['?'], protocol['review_unknown_cells'])
        self.assertIn(f"{counts['1'] + counts['P']} located direct/partial cells", protocol['gap_result'])
        self.assertIn(f"{counts['0']} scoped absences", protocol['gap_result'])
        self.assertEqual('undetermined', review_coverage_status(data['review_gap_matrix']))
        self.assertEqual(protocol['review_direct_coverage_status'],
                         review_coverage_status(data['review_gap_matrix']))

    def test_each_admitted_value_drift_is_rejected(self):
        for key, expected in ADMITTED.items():
            for dimension, (code, _) in expected['cells'].items():
                for wrong in {'0', 'P', '1', '?'} - {code}:
                    data = supplied_data()
                    self.one(data, 'review_gap_matrix', key)[dimension] = wrong
                    with self.subTest(key=key, dimension=dimension, value=wrong):
                        with self.assertRaises(AssertionError):
                            self.check_admissions(data)

    def test_missing_reversed_zero_and_out_of_range_page_locators_rejected(self):
        for key, expected in ADMITTED.items():
            for bad in ('unspecified', '0', '3-2', str(expected['pages'] + 1)):
                data = supplied_data()
                dimension, (_, pages) = next(iter(expected['cells'].items()))
                row = self.one(data, 'review_gap_matrix', key)
                row['source_basis'] = row['source_basis'].replace(
                    dimension + ': PDF pp. ' + pages + ':',
                    dimension + ': PDF pp. ' + bad + ':', 1)
                with self.subTest(key=key, pages=bad):
                    with self.assertRaises((AssertionError, ValueError)):
                        self.check_admissions(data)

    def test_in_range_page_drift_still_requires_review(self):
        data = supplied_data()
        row = self.one(data, 'review_gap_matrix', 'kitchenham')
        row['source_basis'] = row['source_basis'].replace(
            'claim_ceiling_binding: PDF pp. 21-25,30:',
            'claim_ceiling_binding: PDF pp. 21-24,30:')
        with self.assertRaises(AssertionError):
            self.check_admissions(data)

    def test_selected_html_or_legacy_status_cannot_certify_scoped_zeros(self):
        for key in ADMITTED:
            for status in ('selected_fulltext_checked', 'legacy_not_reverified'):
                data = supplied_data()
                self.one(data, 'source_locations', key)['content_check_status'] = status
                with self.subTest(key=key, status=status):
                    with self.assertRaisesRegex(ValueError, 'bound scoped fulltext'):
                        self.check_admissions(data)

    def test_acquisition_without_complete_reader_assessment_is_insufficient(self):
        for key in ADMITTED:
            for defect in ('missing', 'partial', 'independent'):
                data = supplied_data()
                if defect == 'missing':
                    data['semantic_readings'] = [r for r in data['semantic_readings'] if r['bib_key'] != key]
                else:
                    reading = self.one(data, 'semantic_readings', key)
                    if defect == 'partial':
                        reading['reading_extent'] = 'selected_sections'
                    else:
                        reading['independent'] = 'true'
                with self.subTest(key=key, defect=defect):
                    with self.assertRaises((AssertionError, ValueError)):
                        self.check_admissions(data)

    def test_other_source_version_or_changed_coded_fields_cannot_reuse_assessment(self):
        for table, field, value in (
            ('source_readings', 'source_sha256', '0' * 64),
            ('semantic_readings', 'fields_sha256', '0' * 64),
            ('study_extractions', 'observation', 'changed owned negative-control value'),
        ):
            data = supplied_data()
            self.one(data, table, 'wohlin')[field] = value
            with self.subTest(table=table, field=field):
                with self.assertRaises(ValueError):
                    self.check_admissions(data)

    def test_seven_field_bindings_are_not_optional(self):
        data = supplied_data()
        data['field_evidence'] = [r for r in data['field_evidence']
                                  if (r['bib_key'], r['field']) != ('tpl', 'claim_ceiling')]
        with self.assertRaisesRegex(ValueError, 'incomplete seven-field'):
            self.check_admissions(data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
