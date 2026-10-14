import csv
import hashlib
import json
import math
import re
import runpy
import unittest
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from corpus_audit import nonindependent_status, review_coverage_status, content_check_counts, specific_content_locator
from snapshot_evidence import source_count_macros, validate_snapshot_evidence

ROOT = Path(__file__).resolve().parents[1]
LOCKED_CORPUS_SIZE = 97


def dimensions_for_review():
    return ('android_repackaging', 'component_version', 'supply_chain_provenance',
            'authorization_policy', 'behavioral_assurance', 'ai_mediated_workflow',
            'claim_ceiling_binding')


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

    def test_review_matrix_has_no_direct_all_dimension_prior(self):
        dimensions = [
            "android_repackaging", "component_version", "supply_chain_provenance",
            "authorization_policy", "behavioral_assurance", "ai_mediated_workflow",
            "claim_ceiling_binding",
        ]
        self.assertFalse(any(all(row[d] == "1" for d in dimensions) for row in self.reviews))
        self.assertEqual('undetermined', review_coverage_status(self.reviews))

    def test_content_checks_are_distinct_from_legacy_depth_labels(self):
        checked = [r for r in self.source_locations if r['content_check_status'] in
                   {'selected_fulltext_checked', 'complete_scope_checked'}]
        protocol = json.loads((ROOT / 'data/protocol.json').read_text(encoding='utf-8'))
        counts = content_check_counts(self.source_locations)
        self.assertEqual(protocol['content_checked'], len(checked))
        self.assertEqual(protocol['selected_fulltext_checked'], counts['selected_fulltext_checked_records'])
        self.assertEqual(protocol['complete_scope_checked'], counts['complete_scope_checked_records'])
        self.assertEqual(protocol['legacy_not_reverified'], counts['legacy_not_reverified_records'])
        self.assertEqual(LOCKED_CORPUS_SIZE, len(checked) + counts['legacy_not_reverified_records'])
        for row in checked:
            self.assertTrue(row['fulltext_url'].startswith('https://'))
            self.assertTrue(specific_content_locator(row['locations']))
        by_key = {r['bib_key']: r for r in self.source_locations}
        for row in self.reviews:
            if any(row[d] in {'1', 'P'} for d in dimensions_for_review()):
                self.assertIn(by_key[row['bib_key']]['content_check_status'],
                              {'selected_fulltext_checked', 'complete_scope_checked'})

    def test_specific_content_locators_do_not_require_fabricated_pdf_pages(self):
        self.assertTrue(specific_content_locator('Author PDF pp. 3-4: Section 2'))
        self.assertTrue(specific_content_locator('Publisher HTML Sections 1 (Introduction), 4.5 (TPL detection)'))
        for locator in ('DOI record', 'full text checked', 'Publisher HTML abstract',
                        'PDF pp. unspecified', 'linked full text or selected PDF pp. 3'):
            self.assertFalse(specific_content_locator(locator))

    def test_scoped_readings_count_as_checked_without_upgrading_unknowns(self):
        rows = [{'content_check_status': value} for value in
                ('selected_fulltext_checked', 'complete_scope_checked', 'legacy_not_reverified')]
        self.assertEqual({'selected_fulltext_checked_records': 1, 'complete_scope_checked_records': 1,
                          'content_checked_records': 2, 'legacy_not_reverified_records': 1},
                         content_check_counts(rows))

    def test_recheck_fraction_and_same_process_disclosure(self):
        protocol = json.loads((ROOT / 'data/protocol.json').read_text(encoding='utf-8'))
        self.assertEqual(protocol['fresh_source_rechecks'], len(self.rechecks))
        self.assertGreaterEqual(len(self.rechecks), 28)
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
        snapshot = ROOT / "manuscript_snapshot"
        load = lambda path: json.loads(path.read_text(encoding="utf-8"))
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        snapshot_build = load(snapshot / "build-evidence.json")
        snapshot_visual = load(snapshot / "visual-inspection.json")
        result_build = load(ROOT / "results/paper_build_evidence.json")
        result_visual = self.visual_inspection
        snapshot_config = runpy.run_path(str(snapshot / "build.py"))
        counts = content_check_counts(self.source_locations)
        checked = counts["content_checked_records"]
        unchecked = len(self.source_locations) - checked

        macro_paths = {
            "snapshot generated": snapshot / "generated/corpus_counts.tex",
            "default build input": ROOT / "results/tex/corpus_counts.tex",
        }
        primary = None
        paper = ROOT.parent / "paper"
        if paper.is_dir():
            paper_config = runpy.run_path(str(paper / "build.py"))
            primary = {
                "build": load(paper / "build-evidence.json"),
                "source_sha256": paper_config["source_binding"](paper),
                "pdf_sha256": digest(paper / "build/main.pdf"),
                "log_sha256": digest(paper / "build/main.log"),
                "budget": paper_config["MAX_PAGES"],
            }
            macro_paths["primary generated"] = paper / "generated/corpus_counts.tex"
        for name, main_path in (("snapshot main fallback", snapshot / "main.tex"),
                                ("primary main fallback", paper / "main.tex")):
            if main_path.is_file():
                value = source_count_macros(main_path.read_text(encoding="utf-8"))
                if value is not None:
                    macro_paths[name] = main_path
        macro_counts = {
            name: source_count_macros(path.read_text(encoding="utf-8"))
            for name, path in macro_paths.items()
        }
        validate_snapshot_evidence(
            build=snapshot_build, visual=snapshot_visual,
            result_build=result_build, result_visual=result_visual,
            budget=snapshot_config["MAX_PAGES"],
            source_sha256=snapshot_config["source_binding"](snapshot),
            pdf_sha256=digest(snapshot / "build/main.pdf"),
            log_sha256=digest(snapshot / "build/main.log"),
            checked=checked, unchecked=unchecked,
            macro_counts=macro_counts, primary=primary,
        )

    def test_material_claim_ledger_complete(self):
        self.assertTrue(self.material_claims)
        self.assertEqual(len(self.material_claims), len({r["claim_id"] for r in self.material_claims}))
        required = [
            "claim", "source_or_input", "proof_or_checker", "raw_result",
            "maturity", "fresh_recheck_and_boundary",
        ]
        for row in self.material_claims:
            self.assertTrue(all(row[field].strip() for field in required))

    def test_current_material_claim_counts_match_data_and_build(self):
        claims = {r['claim_id']: r for r in self.material_claims}
        normalized = lambda value: re.sub(r'\s+', '', value.lower())
        counts = content_check_counts(self.source_locations)
        cells = Counter(r[d] for r in self.reviews for d in dimensions_for_review())
        semantic = read_csv('data/semantic_readings.csv')
        field_rows = read_csv('data/field_evidence.csv')
        checks = {
            'C04': (f"{counts['content_checked_records']} records", f"{counts['selected_fulltext_checked_records']} selected HTML", f"{counts['complete_scope_checked_records']} complete-scoped PDF"),
            'C05': (f"{len(self.reviews)}-record", f"{cells['?']} unresolved cells"),
            'C06': (f"{len(self.rechecks)} entries", f"checks {counts['content_checked_records']} works"),
            'C17': (f"cover {counts['content_checked_records']} records",),
            'C29': (f"{len(semantic)} complete", f"{len(field_rows)} supplementary", f"{7*len(self.extractions)} possible fields"),
        }
        for claim_id, parts in checks.items():
            for part in parts:
                with self.subTest(claim=claim_id, part=part):
                    self.assertIn(normalized(part), normalized(claims[claim_id]['claim']))
        snapshot = ROOT / 'manuscript_snapshot'
        config = runpy.run_path(str(snapshot / 'build.py'))
        build = json.loads((snapshot / 'build-evidence.json').read_text(encoding='utf-8'))
        self.assertIn(normalized(f"upper bound of {config['MAX_PAGES']} pages"), normalized(claims['C27']['claim']))
        self.assertIn(normalized(f"{build['pages']}-page PDF"), normalized(claims['C28']['claim']))

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
