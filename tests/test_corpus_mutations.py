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


if __name__ == "__main__":
    unittest.main(verbosity=2)
