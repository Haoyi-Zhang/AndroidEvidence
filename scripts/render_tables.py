"""Derive manuscript-facing TeX fragments from audited, local ledgers."""
from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main(results=None):
    results = Path(results) if results is not None else ROOT / 'results'
    result = json.loads((results / "coverage_result.json").read_text(encoding="utf-8"))
    corpus_summary = json.loads((results / "corpus_summary.json").read_text(encoding="utf-8"))
    if corpus_summary['status'] != 'passed':
        raise ValueError('failed corpus audit cannot generate manuscript tables')
    records = {r["record_id"]: r for r in read_csv(ROOT / "data/records.csv")}
    cells = {(r["record_id"], r["obligation_id"]): r["value"] for r in read_csv(ROOT / "data/coverage.csv")}
    review_rows = read_csv(ROOT / "data/review_gap_matrix.csv")

    out = results / "tex"
    out.mkdir(exist_ok=True)

    counts = result["record_counts"]
    recheck = result["recheck"]
    macros = {
        "SelectedRecords": counts["selected_scholarly"],
        "ReviewRecords": counts["review_records"],
        "BaseReviews": counts["base_eligible_reviews"],
        "MainCorpus": counts["main_primary_corpus"],
        "PositiveCells": counts["positive_cells"],
        "UnknownCells": counts["unknown_cells"],
        "CoverageCells": counts["coverage_cells"],
        "ExtractionUnits": counts["extractions"],
        "RecheckedCells": recheck["completed_cells"],
        "RecheckedPercent": f"{100 * recheck['fraction']:.1f}",
    }
    (out / "counts.tex").write_text(
        "".join("\\newcommand{\\" + k + "}{" + str(v) + "}\n" for k, v in macros.items()),
        encoding="utf-8",
    )

    rows = []
    for rid in ("R01", "R02", "R03", "R04"):
        values = [cells[rid, "O" + str(j)] for j in range(1, 8)]
        rows.append(rid + r" \cite{" + records[rid]["bib_key"] + "} & " + " & ".join(values) + r" \\")
    rows.append(r"Other base records & ? & ? & ? & ? & ? & ? & ? \\")
    (out / "coverage_rows.tex").write_text(
        "\\begin{tabular}{lccccccc}\n\\toprule\nReview record & O1 & O2 & O3 & O4 & O5 & O6 & O7 \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n",
        encoding="utf-8",
    )

    rows = []
    labels = {
        "base_coarse": "Base; six coarse obligations",
        "core_only_coarse": "Core only; six coarse obligations",
        "publication_documented_coarse": "Publication documented; six coarse",
        "leave_out_R03": "Base without R03; six coarse",
        "base_all": "Base; all seven obligations",
    }
    for key, label in labels.items():
        x = result["analyses"][key]
        rows.append(f"{label} & {x['rows']} & {x['direct']} & {x['mosaic']}" + r" \\")
    (out / "sensitivity_rows.tex").write_text(
        "\\begin{tabular}{p{5.1cm}rll}\n\\toprule\nSelection & Reviews & Direct & Mosaic \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n",
        encoding="utf-8",
    )

    # A compact, data-derived adversary table for the paper. The full 21-row
    # matrix remains in data/review_gap_matrix.csv.
    selected = {
        "repack", "wurepack2026", "tpl", "zengtpsurvey2024", "astra",
        "properties", "reichert2024", "williams2025", "cyberrisk2026", "gokkaya2026",
    }
    dimensions = [
        "android_repackaging", "component_version", "supply_chain_provenance",
        "authorization_policy", "behavioral_assurance", "ai_mediated_workflow",
        "claim_ceiling_binding",
    ]
    matrix_lines = []
    for row in review_rows:
        if row["bib_key"] in selected:
            matrix_lines.append(
                r"\cite{" + row["bib_key"] + "} & "
                + " & ".join(row[d] for d in dimensions)
                + r" \\"
            )
    (out / "review_matrix_rows.tex").write_text("\n".join(matrix_lines) + "\n", encoding="utf-8")

    oracle = json.loads((results / "oracle_result.json").read_text(encoding="utf-8"))
    (out / "oracle.tex").write_text(
        "\\newcommand{\\OracleMatrices}{" + format(oracle["ternary_matrices"], ",") + "}\n"
        + "\\newcommand{\\OracleCompletions}{" + format(oracle["binary_completions_across_matrices"], ",") + "}\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "generated",
        "full_review_matrix_rows": len(review_rows),
        "paper_review_matrix_rows": len(matrix_lines),
        "corpus_records": corpus_summary["records"],
    }, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path)
    main(parser.parse_args().results)
