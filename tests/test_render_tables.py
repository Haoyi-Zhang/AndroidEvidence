"""Portable display-selection regression; no private stage or historical code."""
import copy
import csv
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import render_tables

# Named independent fixture of the ten displayed key/cell vectors. This checks
# formatting and selection only, not correctness of literature interpretation.
DISPLAY = (
    ("repack", "1 P 0 0 P 0 P"), ("tpl", "P 1 0 0 P 0 P"),
    ("astra", "0 P 1 1 P 0 P"), ("properties", "0 P 1 1 P 0 P"),
    ("wurepack2026", "1 P 0 0 P 0 P"), ("zengtpsurvey2024", "0 1 P P P 0 P"),
    ("reichert2024", "0 P 1 P P 0 P"), ("williams2025", "0 P 1 P P P P"),
    ("cyberrisk2026", "0 P P P P 0 P"), ("gokkaya2026", "0 P 1 P P 0 P"),
)
COLUMNS = ("android_repackaging", "component_version", "supply_chain_provenance",
           "authorization_policy", "behavioral_assurance", "ai_mediated_workflow",
           "claim_ceiling_binding")


def supplied_rows():
    path = Path(__file__).resolve().parents[1] / "data/review_gap_matrix.csv"
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def display_reference(rows):
    output = []
    for key, _ in DISPLAY:
        matching = [row for row in rows if row["bib_key"] == key]
        if len(matching) != 1:
            raise ValueError(key)
        cells = [matching[0][column] for column in COLUMNS]
        if not set(cells) <= {"0", "P", "1", "?"}:
            raise ValueError(key)
        output.append("\\cite{" + key + "} & " + " & ".join(cells) + " \\\\")
    return output


def generation_fixture(review_rows):
    """Small explicit inputs for all existing generator branches."""
    records = [{"record_id": "R" + str(i).zfill(2), "bib_key": key}
               for i, (key, _) in enumerate(DISPLAY[:4], 1)]
    coverage = [{"record_id": r["record_id"], "obligation_id": "O" + str(j), "value": "?"}
                for r in records for j in range(1, 8)]
    record_counts = dict(selected_scholarly=4, review_records=4, base_eligible_reviews=4,
                         main_primary_corpus=0, positive_cells=0, unknown_cells=28,
                         coverage_cells=28, extractions=4)
    result = {"record_counts": record_counts, "recheck": {"completed_cells": 1, "fraction": 0.25},
              "analyses": {name: {"rows": 4, "direct": "undetermined", "mosaic": "undetermined"}
                           for name in ("base_coarse", "core_only_coarse",
                                        "publication_documented_coarse", "leave_out_R03", "base_all")}}
    inputs = {"coverage_result.json": result, "corpus_summary.json": {"status": "passed", "records": 97},
              "oracle_result.json": {"ternary_matrices": 19683,
                                     "binary_completions_across_matrices": 262144}}
    ledgers = {"records.csv": records, "coverage.csv": coverage,
               "review_gap_matrix.csv": review_rows}
    return inputs, ledgers


def run_generator(module, rows, corpus_status="passed"):
    inputs, ledgers = generation_fixture(rows)
    inputs["corpus_summary.json"]["status"] = corpus_status
    with tempfile.TemporaryDirectory() as folder:
        with mock.patch.object(Path, "read_text", lambda path, **kwargs: json.dumps(inputs[path.name])):
            with mock.patch.object(module, "read_csv", lambda path: copy.deepcopy(ledgers[path.name])):
                with mock.patch("builtins.print"):
                    module.main(Path(folder))
        return {p.name: p.read_bytes() for p in (Path(folder) / "tex").iterdir()}


class DisplayRowsRegression(unittest.TestCase):
    def test_supplied_21_rows_and_literal_display_fixture(self):
        rows = supplied_rows()
        snapshot = copy.deepcopy(rows)
        self.assertEqual(len(rows), 21)
        expected = ["\\cite{" + key + "} & " + " & ".join(cells.split()) + " \\\\"
                    for key, cells in DISPLAY]
        self.assertEqual(render_tables.review_matrix_lines(rows), expected)
        self.assertEqual(display_reference(rows), expected)
        self.assertEqual(rows, snapshot)

    def test_selected_cells_preserve_all_four_codes(self):
        for key, _ in DISPLAY:
            for column in COLUMNS:
                for value in ("0", "P", "1", "?"):
                    rows = supplied_rows()
                    next(r for r in rows if r["bib_key"] == key)[column] = value
                    with self.subTest(key=key, column=column, value=value):
                        self.assertEqual(render_tables.review_matrix_lines(rows), display_reference(rows))

    def test_declared_order_is_independent_of_container_order(self):
        rows = supplied_rows()
        expected = display_reference(rows)
        for shift in range(len(rows)):
            self.assertEqual(render_tables.review_matrix_lines(rows[shift:] + rows[:shift]), expected)
        self.assertEqual(render_tables.review_matrix_lines(list(reversed(rows))), expected)
        extra = dict(rows[0], bib_key="unselected-owned-control")
        self.assertEqual(render_tables.review_matrix_lines([extra] + rows), expected)

    def test_missing_and_duplicate_selected_rows_fail_closed(self):
        rows = supplied_rows()
        for key, _ in DISPLAY:
            missing = [r for r in rows if r["bib_key"] != key]
            duplicate = rows + [copy.deepcopy(next(r for r in rows if r["bib_key"] == key))]
            for changed in (missing, duplicate):
                with self.subTest(key=key):
                    with self.assertRaisesRegex(ValueError, "exactly one row for key: " + key):
                        render_tables.review_matrix_lines(changed)
                    with mock.patch.object(Path, "write_text", side_effect=AssertionError("unexpected fragment write")):
                        with self.assertRaisesRegex(ValueError, "exactly one row for key: " + key):
                            run_generator(render_tables, changed)
        for invalid in ("", "2", "P ", None, True):
            changed = copy.deepcopy(rows)
            changed[0][COLUMNS[0]] = invalid
            with self.assertRaisesRegex(ValueError, "invalid displayed review cell"):
                render_tables.review_matrix_lines(changed)

    def test_complete_generator_outputs_include_reference_rows(self):
        outputs = run_generator(render_tables, supplied_rows())
        self.assertEqual(set(outputs), {"counts.tex", "coverage_rows.tex", "sensitivity_rows.tex",
                                       "review_matrix_rows.tex", "oracle.tex"})
        # The existing writer uses text-mode native line endings; compare exact
        # platform bytes, not a normalized or weakened output comparison.
        expected = os.linesep.join(display_reference(supplied_rows())) + os.linesep
        self.assertEqual(outputs["review_matrix_rows.tex"], expected.encode("utf-8"))
        self.assertIn(b"\\newcommand{\\OracleMatrices}{19,683}", outputs["oracle.tex"])
        self.assertIn(b"\\newcommand{\\SelectedRecords}{4}", outputs["counts.tex"])

    def test_failed_corpus_audit_cannot_emit_fragments(self):
        with self.assertRaisesRegex(ValueError, "failed corpus audit"):
            run_generator(render_tables, supplied_rows(), corpus_status="failed")


if __name__ == "__main__":
    unittest.main()
