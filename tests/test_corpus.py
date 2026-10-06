import csv
import json
import math
import re
import unittest
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from corpus_audit import nonindependent_status

ROOT = Path(__file__).resolve().parents[1]
LOCKED_CORPUS_SIZE = 97


def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("data/corpus.csv")
        cls.extractions = read_csv("data/study_extractions.csv")
        cls.reviews = read_csv("data/review_gap_matrix.csv")
        cls.rechecks = read_csv("data/source_rechecks.csv")
        cls.screening = read_csv("data/screening_ledger.csv")
        cls.source_locations = read_csv("data/source_locations.csv")
        cls.search_provenance = read_csv("data/search_provenance.csv")
        cls.bib_verify = read_csv("data/bibliography_verification.csv")
        cls.excluded = read_csv("data/excluded_publications.csv")
        cls.calibration = read_csv("data/calibration_papers.csv")
        cls.unresolved_leads = read_csv("data/unresolved_leads.csv")
        cls.resolved_leads = read_csv("data/resolved_leads.csv")
        cls.claims = read_csv("data/synthesis_claims.csv")
        cls.material_claims = read_csv("claim_evidence_ledger.csv")
        cls.external_resources = read_csv("external_resources.csv")
        cls.visual_inspection = json.loads((ROOT / "results/visual-inspection.json").read_text(encoding="utf-8"))
        cls.bib_text = (ROOT / "data/references.bib").read_text(encoding="utf-8")
        cls.bib_keys = re.findall(r"^@\w+\{([^,]+),", cls.bib_text, re.M)

    def test_exact_corpus_bibliography_extraction_binding(self):
        corpus_keys = [r["bib_key"] for r in self.rows]
        extraction_keys = [r["bib_key"] for r in self.extractions]
        self.assertEqual(LOCKED_CORPUS_SIZE, len(corpus_keys))
        self.assertEqual(len(corpus_keys), len(set(corpus_keys)))
        self.assertEqual(LOCKED_CORPUS_SIZE, len(self.bib_keys))
        self.assertEqual(set(corpus_keys), set(self.bib_keys))
        self.assertEqual(set(corpus_keys), set(extraction_keys))
        self.assertEqual(LOCKED_CORPUS_SIZE, len(set(extraction_keys)))

    def test_primary_review_and_publication_obligations(self):
        roles = Counter(r["role"] for r in self.rows)
        publication = Counter(r["publication_evidence"] for r in self.rows)
        self.assertEqual(Counter({"primary_or_system": 76, "secondary_or_method": 21}), roles)
        self.assertTrue(60 <= roles["primary_or_system"] <= 140)
        primary_venue = sum(
            r["role"] == "primary_or_system" and r["publication_evidence"] == "venue_recorded"
            for r in self.rows
        )
        self.assertEqual(74, primary_venue)
        self.assertGreaterEqual(primary_venue, 60)
        self.assertEqual(
            Counter({"venue_recorded": 93, "preprint_record": 3, "technical_method_report": 1}),
            publication,
        )
        self.assertEqual(21, len(self.reviews))
        self.assertGreaterEqual(len(self.reviews), 12)

    def test_strata_and_depths(self):
        self.assertEqual(
            Counter({
                "android_artifact": 34,
                "review_and_method": 21,
                "third_party_library": 17,
                "supply_chain": 17,
                "ai_mediated": 8,
            }),
            Counter(r["stratum"] for r in self.rows),
        )
        self.assertEqual(
            Counter({"full_or_selected_source": 61, "publisher_abstract_or_selected_source": 36}),
            Counter(r["reading_depth"] for r in self.rows),
        )

    def test_each_extraction_is_bound_and_has_limits(self):
        self.assertEqual(LOCKED_CORPUS_SIZE, len(self.extractions))
        by_key = {r["bib_key"]: r for r in self.rows}
        for row in self.extractions:
            corpus = by_key[row["bib_key"]]
            self.assertEqual(corpus["record_id"], row["record_id"])
            self.assertEqual(corpus["reading_depth"], row["reading_depth"])
            self.assertEqual(corpus["source_url_or_access_note"], row["source_url_or_access_note"])
            self.assertTrue(row["observation"].strip())
            self.assertTrue(row["counter_history"].strip())
            self.assertTrue(row["inference_limit"].strip())
            self.assertTrue(nonindependent_status(row['verification_status']))

    def test_no_retired_template_observations(self):
        prefixes = (
            "The work organizes, reviews, or methodologically structures",
            "The work analyzes Android artifacts using the feature family indicated by its title and venue record",
            "The work analyzes library regions, families, versions, updates, or vulnerability links",
            "The work reports repository, signing, attestation, transparency, build, CI, or package-ecosystem evidence",
            "The work reports generated-code, assistant interaction, dependency recommendation, mobile generation, privacy, or security evidence",
        )
        stale = [r["bib_key"] for r in self.extractions if r["observation"].startswith(prefixes)]
        self.assertEqual([], stale)
        self.assertFalse(any('Source: “' in r["observation"] for r in self.extractions))

    def test_source_location_ledger_exactly_binds_corpus(self):
        corpus_keys = {r["bib_key"] for r in self.rows}
        corpus_ids = {r["record_id"] for r in self.rows}
        self.assertEqual(LOCKED_CORPUS_SIZE, len(self.source_locations))
        self.assertEqual(corpus_keys, {r["bib_key"] for r in self.source_locations})
        self.assertEqual(corpus_ids, {r["record_id"] for r in self.source_locations})
        self.assertEqual(LOCKED_CORPUS_SIZE, len({r["consumed_source_url"] for r in self.source_locations}))
        for row in self.source_locations:
            self.assertTrue(row["locations"].strip())
            self.assertTrue(row["verification_route"].strip())
            self.assertTrue(
                "not necessarily cover-to-cover" in row["reading_boundary"]
                or "no full-text completeness claim" in row["reading_boundary"]
            )

    def test_retained_record_provenance_is_exact_and_bounded(self):
        corpus_keys = {r["bib_key"] for r in self.rows}
        self.assertEqual(LOCKED_CORPUS_SIZE, len(self.search_provenance))
        self.assertEqual(corpus_keys, {r["bib_key"] for r in self.search_provenance})
        for row in self.search_provenance:
            self.assertTrue(row["discovery_route"].strip())
            self.assertIn("not a complete database-search hit denominator", row["denominator_scope"])
            self.assertIn("retrospective", row["reconstruction_status"])

    def test_bibliography_status_ledger_and_quarantine(self):
        corpus_keys = {r["bib_key"] for r in self.rows}
        self.assertEqual(LOCKED_CORPUS_SIZE, len(self.bib_verify))
        self.assertEqual(corpus_keys, {r["bib_key"] for r in self.bib_verify})
        identifiers = [r["canonical_identifier"] for r in self.bib_verify]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(r["included_status"] == "eligible_current_record" for r in self.bib_verify))
        self.assertFalse(any(
            token in " ".join(r.values()).lower()
            for r in self.bib_verify for token in ("withdrawn", "retracted")
        ))
        excluded_keys = {r["bib_key"] for r in self.excluded}
        self.assertIn("sbomslr2025", excluded_keys)
        self.assertFalse(excluded_keys & corpus_keys)
        active_paths = (
            "data/references.bib", "data/corpus.csv", "data/study_extractions.csv",
            "data/review_gap_matrix.csv", "data/source_rechecks.csv", "data/synthesis_claims.csv",
        )
        active_text = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in active_paths)
        self.assertNotIn("sbomslr2025", active_text)

    def test_calibration_contract(self):
        self.assertEqual(22, len(self.calibration))
        self.assertEqual(
            Counter({"closest": 12, "influential_method": 5, "adjacent_evidence": 5}),
            Counter(r["group"] for r in self.calibration),
        )
        keys = [r["bib_key"] for r in self.calibration]
        self.assertEqual(len(keys), len(set(keys)))
        by_key = {r["bib_key"]: r for r in self.rows}
        for row in self.calibration:
            self.assertEqual("full_or_selected_source", by_key[row["bib_key"]]["reading_depth"])
            self.assertTrue(row["narrative_sequence"].strip())
            self.assertTrue(row["figure_table_role"].strip())
            self.assertTrue(row["limitation"].strip())

    def test_review_matrix_has_no_direct_all_dimension_prior(self):
        dimensions = [
            "android_repackaging", "component_version", "supply_chain_provenance",
            "authorization_policy", "behavioral_assurance", "ai_mediated_workflow",
            "claim_ceiling_binding",
        ]
        self.assertFalse(any(all(row[d] == "1" for d in dimensions) for row in self.reviews))

    def test_recheck_fraction_and_same_process_disclosure(self):
        self.assertEqual(26, len(self.rechecks))
        self.assertGreaterEqual(len(self.rechecks), math.ceil(0.15 * len(self.extractions)))
        self.assertTrue(all(r["independent"] == "false" for r in self.rechecks))
        self.assertEqual(len(self.rechecks), len({r["bib_key"] for r in self.rechecks}))
        by_key = {r["bib_key"]: r for r in self.rows}
        for row in self.rechecks:
            self.assertEqual(by_key[row["bib_key"]]["source_url_or_access_note"], row["source_url_or_access_note"])

    def test_screening_binds_retained_and_excluded_records(self):
        included = [r["bib_key"] for r in self.screening if r["decision"] == "include"]
        self.assertEqual({r["bib_key"] for r in self.rows}, set(included))
        self.assertEqual(len(included), len(set(included)))
        excluded_screen = {r["bib_key"] for r in self.screening if r["decision"].startswith("exclude")}
        self.assertTrue({r["bib_key"] for r in self.excluded} <= excluded_screen)
        self.assertLessEqual(len(self.screening), 450)

    def test_stale_leads_are_resolved(self):
        self.assertEqual([], self.unresolved_leads)
        self.assertEqual(
            {"staticandroid", "sufatrio", "xuandroid"},
            {r["bib_key"] for r in self.resolved_leads},
        )

    def test_external_resource_ledger_exactly_binds_scholarly_records(self):
        scholarly = [r for r in self.external_resources if r["resource_type"].startswith("scholarly_")]
        self.assertEqual(LOCKED_CORPUS_SIZE, len(scholarly))
        self.assertEqual(
            Counter(r["source_url_or_access_note"] for r in self.rows),
            Counter(r["scholarly_or_official_url"] for r in scholarly),
        )


    def test_visual_inspection_evidence(self):
        v = self.visual_inspection
        self.assertEqual("passed", v["status"])
        self.assertEqual(35, v["page_count"])
        self.assertTrue(v["all_pages_inspected"])
        self.assertEqual([5, 8, 21, 26, 28, 35], v["full_size_pages_inspected"])
        self.assertTrue(all(value == 0 for value in v["findings"].values()))
        self.assertEqual("consistent", v["renderer_parity"]["assessment"])
        self.assertGreaterEqual(v["renderer_parity"]["min_pdftoppm_ink_coverage"], 0.99)
        self.assertGreaterEqual(v["renderer_parity"]["min_pdfium_ink_coverage"], 0.99)

    def test_material_claim_ledger_complete(self):
        self.assertGreaterEqual(len(self.material_claims), 28)
        self.assertEqual(len(self.material_claims), len({r["claim_id"] for r in self.material_claims}))
        required = [
            "claim", "source_or_input", "proof_or_checker", "raw_result",
            "maturity", "fresh_recheck_and_boundary",
        ]
        for row in self.material_claims:
            self.assertTrue(all(row[field].strip() for field in required))

    def test_synthesis_claim_sources_are_bound(self):
        known = set(self.bib_keys)
        self.assertEqual(7, len(self.claims))
        for claim in self.claims:
            supporting = {k.strip() for k in claim["supporting_bib_keys"].split(";") if k.strip()}
            self.assertTrue(supporting)
            self.assertFalse(supporting - known)
            self.assertTrue(claim["counter_history"].strip())
            self.assertTrue(claim["boundary"].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
