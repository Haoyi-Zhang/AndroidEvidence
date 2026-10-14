import contextlib
import csv
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corpus_audit  # noqa: E402


class CorpusMutationControls(unittest.TestCase):
    def run_mutation(self, relative_path, mutate, expected_error=None):
        with tempfile.TemporaryDirectory(prefix="mobile-corpus-") as folder:
            temp = Path(folder) / "artifact"
            shutil.copytree(ROOT, temp)
            path = temp / relative_path
            with patch.object(corpus_audit, 'ROOT', temp), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, corpus_audit.main(), 'positive control must pass before mutation')
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
                fields = list(rows[0])
            mutate(rows)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            captured = io.StringIO()
            with patch.object(corpus_audit, "ROOT", temp), contextlib.redirect_stdout(captured):
                self.assertEqual(1, corpus_audit.main())
            if expected_error is not None:
                errors = json.loads(captured.getvalue())['errors']
                self.assertTrue(any(expected_error in error for error in errors), errors)

    def test_withdrawn_status_cannot_enter_active_verification_ledger(self):
        def mutate(rows):
            rows[0]["version_status"] = "withdrawn"
        self.run_mutation("data/bibliography_verification.csv", mutate)

    def test_duplicate_canonical_identifier_is_rejected(self):
        def mutate(rows):
            rows[1]["canonical_identifier"] = rows[0]["canonical_identifier"]
        self.run_mutation("data/bibliography_verification.csv", mutate)

    def test_excluded_key_cannot_leak_into_active_corpus(self):
        def mutate(rows):
            rows[0]["bib_key"] = "sbomslr2025"
        self.run_mutation("data/corpus.csv", mutate)

    def test_publication_type_disagreement_is_rejected(self):
        def mutate(rows):
            row = next(r for r in rows if r["publication_evidence"] == "preprint_record")
            row["publication_evidence"] = "venue_recorded"
        self.run_mutation("data/corpus.csv", mutate)

    def test_corpus_title_drift_is_rejected(self):
        def mutate(rows):
            rows[0]["title"] += " altered"
        self.run_mutation("data/corpus.csv", mutate)

    def test_corpus_year_drift_is_rejected(self):
        def mutate(rows):
            rows[0]["year"] = "1999"
        self.run_mutation("data/corpus.csv", mutate)

    def test_doi_canonical_url_drift_is_rejected(self):
        def mutate(rows):
            row = next(r for r in rows if r["canonical_identifier"].startswith("doi:"))
            row["canonical_record_url"] = "https://example.org/not-the-doi"
        self.run_mutation("data/bibliography_verification.csv", mutate)

    def test_duplicate_review_cannot_replace_another_source(self):
        self.run_mutation('data/review_gap_matrix.csv', lambda rows: rows.__setitem__(1, dict(rows[0])))

    def test_review_record_id_must_match_key(self):
        def mutate(rows):
            rows[0]['record_id'] = 'W002'
        self.run_mutation('data/review_gap_matrix.csv', mutate)

    def test_independent_claim_cannot_override_single_extractor(self):
        def mutate(rows):
            rows[0]['verification_status'] = 'single_extractor; independent=true'
        self.run_mutation('data/study_extractions.csv', mutate)

    def test_stale_recheck_ceiling_is_rejected(self):
        def mutate(rows):
            rows[0]['rechecked_ceiling'] = 'L6 universally safe'
        self.run_mutation('data/source_rechecks.csv', mutate)

    def test_recheck_record_id_must_match_key(self):
        def mutate(rows):
            rows[0]['record_id'] = 'W001'
        self.run_mutation('data/source_rechecks.csv', mutate)

    def test_failed_audit_does_not_publish_count_fragment(self):
        with tempfile.TemporaryDirectory(prefix='mobile-failed-audit-') as folder:
            temp = Path(folder) / 'artifact'
            shutil.copytree(ROOT, temp)
            with patch.object(corpus_audit, 'ROOT', temp), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, corpus_audit.main(Path(folder) / 'positive-output'))
            path = temp / 'data/corpus.csv'
            with path.open(newline='', encoding='utf-8') as handle:
                rows = list(csv.DictReader(handle))
            rows[0]['title'] += ' altered'
            with path.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            out = Path(folder) / 'attempt-output'
            with patch.object(corpus_audit, 'ROOT', temp), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, corpus_audit.main(out))
            self.assertTrue((out / 'corpus_summary.json').is_file())
            self.assertFalse((out / 'tex/corpus_counts.tex').exists())

    def test_generic_locator_cannot_be_promoted_to_checked_content(self):
        def mutate(rows):
            rows[0]['locations'] = 'linked full text or selected substantive source passages'
        self.run_mutation('data/source_locations.csv', mutate)

    def test_checked_content_requires_actual_fulltext_url(self):
        def mutate(rows):
            rows[0]['fulltext_url'] = ''
        self.run_mutation('data/source_locations.csv', mutate)

    def test_checked_extraction_must_use_its_bound_content_locator(self):
        def mutate(rows):
            row = next(r for r in rows if r['bib_key'] == 'libscout')
            row['source_location'] = 'Publisher record and category-level library summary'
        self.run_mutation('data/study_extractions.csv', mutate)

    def test_checked_extraction_cannot_point_to_another_primary_pdf(self):
        def mutate(rows):
            row = next(r for r in rows if r['bib_key'] == 'libscout')
            row['source_location'] += '; https://example.org/another-owned-fixture.pdf'
        self.run_mutation('data/study_extractions.csv', mutate)

    def test_coding_value_drift_requires_field_evidence_update(self):
        def mutate(rows):
            next(r for r in rows if r['bib_key'] == 'libscout')['observation'] += ' extra unsupported conclusion'
        self.run_mutation('data/study_extractions.csv', mutate)

    def test_duplicate_field_evidence_is_rejected_in_full_workflow(self):
        self.run_mutation('data/field_evidence.csv', lambda rows: rows.append(dict(rows[0])))

    def test_incomplete_field_evidence_is_rejected_in_full_workflow(self):
        self.run_mutation('data/field_evidence.csv', lambda rows: rows.pop())

    def test_positive_review_cannot_use_unverified_fulltext(self):
        def mutate(rows):
            # Keep the existing positive matrix cell, but remove its content
            # certificate in the disposable fixture. Source-reading progress
            # must not silently turn this negative control into a valid case.
            row = next(r for r in rows if r['bib_key'] == 'repack')
            self.assertIn(row['content_check_status'], {'selected_fulltext_checked', 'complete_scope_checked'})
            row['content_check_status'] = 'legacy_not_reverified'
        self.run_mutation('data/source_locations.csv', mutate)

    def test_selected_sections_cannot_certify_absence(self):
        def mutate(rows):
            # Explicitly downgrade a complete-scope absence source in the owned
            # disposable fixture. This does not depend on a real paper remaining
            # unread, or on the supplement's separate complete-reading guard.
            row = next(r for r in rows if r['bib_key'] == 'repack')
            self.assertEqual('complete_scope_checked', row['content_check_status'])
            row['content_check_status'] = 'selected_fulltext_checked'
        self.run_mutation('data/source_locations.csv', mutate,
                          expected_error='absence lacks complete scoped reading')

    def test_historical_transition_cannot_rewrite_the_old_ceiling(self):
        def mutate(rows):
            rows[0]['previous_ceiling'] += ' invented past'
        self.run_mutation('data/recoding_transitions.csv', mutate)

    def test_historical_transition_requires_exact_current_ceiling(self):
        def mutate(rows):
            rows[0]['current_ceiling'] += ' unsupported current'
        self.run_mutation('data/recoding_transitions.csv', mutate)

    def test_transition_requires_the_read_source_version(self):
        def mutate(rows):
            rows[0]['source_sha256'] = '0' * 64
        self.run_mutation('data/recoding_transitions.csv', mutate)

    def test_transition_cannot_backdate_new_reading(self):
        def mutate(rows):
            rows[0]['recoding_date'] = '2026-10-11'
        self.run_mutation('data/recoding_transitions.csv', mutate)

    def test_duplicate_transition_is_rejected(self):
        self.run_mutation('data/recoding_transitions.csv', lambda rows: rows.append(dict(rows[0])))


if __name__ == "__main__":
    unittest.main(verbosity=2)
