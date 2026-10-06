import contextlib
import csv
import io
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
    def run_mutation(self, relative_path, mutate):
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
            with patch.object(corpus_audit, "ROOT", temp), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, corpus_audit.main())

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

    def test_calibration_group_count_is_locked(self):
        def mutate(rows):
            rows[0]["group"] = "adjacent_evidence"
        self.run_mutation("data/calibration_papers.csv", mutate)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
