"""Build and preflight the single-column ACM review manuscript."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
try:
    import resource
except ImportError:
    resource = None
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT.parent if ROOT.name == "manuscript_snapshot" else ROOT.parent / "artifact"
MAX_PAGES = 36


def source_binding(root):
    """Bind only active TeX inputs, the bibliography and publisher template."""
    root = Path(root).resolve()
    pending = [root / "main.tex"]
    inputs = set()
    while pending:
        path = pending.pop().resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or out-of-tree manuscript input: {path}")
        if path in inputs:
            continue
        inputs.add(path)
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)(?<!\\)%.*$", "", text)
        for braced, bare in re.findall(r"\\input\s*(?:\{([^{}]+)\}|([^\s{}%]+))", text):
            child = root / (braced or bare)
            pending.append(child if child.suffix else child.with_suffix(".tex"))
    inputs.update(root / name for name in ("references.bib", "acmart.cls", "ACM-Reference-Format.bst"))
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(inputs)}


def check_current_binding(root, pdf):
    """Reject stale PDFs/logs instead of accepting them by page count alone."""
    root = Path(root)
    evidence = json.loads((root / "build-evidence.json").read_text(encoding="utf-8"))
    if evidence.get("status") != "passed" or evidence.get("source_sha256") != source_binding(root):
        raise ValueError("Build evidence does not bind the active manuscript source.")
    if evidence.get("pdf_sha256") != hashlib.sha256(Path(pdf).read_bytes()).hexdigest():
        raise ValueError("PDF differs from the current build binding; rebuild the manuscript.")
    log = root / "build/main.log"
    if evidence.get("log_sha256") != hashlib.sha256(log.read_bytes()).hexdigest():
        raise ValueError("Final LaTeX log differs from the current build binding.")
    return evidence


def run(cmd, *, cwd, env, out_path, timeout=45):
    before = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    start = time.perf_counter()
    with out_path.open("w", encoding="utf-8") as out:
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                stdout=out,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SystemExit(f"Build command timed out: {' '.join(cmd)}") from exc
    after = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    return result.returncode, {
        "command": [Path(cmd[0]).name, *cmd[1:]],
        "exit_code": result.returncode,
        "wall_seconds": time.perf_counter() - start,
        "child_cpu_seconds": (after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime) if after else None,
        "cumulative_max_child_rss_kib": after.ru_maxrss if after else None,
    }


def main(results=None) -> None:
    pdflatex = shutil.which("pdflatex")
    bib = shutil.which("bibtex") or shutil.which("bibtex8")
    pdfinfo = shutil.which("pdfinfo")
    if not pdflatex or not bib or not pdfinfo:
        raise SystemExit("Requires pdflatex, bibtex/bibtex8, and pdfinfo.")

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1")

    # Preserve the supplied class, fonts, margins and scientific content.
    # Unassigned DOI, reference and copyright furniture may be suppressed;
    # their removal is not a scientific-layout manipulation.
    source_text = (ROOT / "main.tex").read_text(encoding="utf-8")
    required_class = r"\documentclass[manuscript,screen,review]{acmart}"
    if required_class not in source_text:
        raise SystemExit("main.tex must use the single-column manuscript,screen,review class contract.")
    forbidden_source_patterns = {
        "nonacm class option": "nonacm",
        "CCS suppression": "printccs=false",
        "manual geometry override": r"\geometry",
        "manual text-width override": r"\textwidth",
        "manual margin override": r"\oddsidemargin",
        "manual font-size override": r"\fontsize",
        "negative vertical spacing": r"\vspace{-",
        "negative vertical skip": r"\vskip-",
    }
    found_forbidden = [name for name, pattern in forbidden_source_patterns.items() if pattern in source_text]
    if found_forbidden:
        raise SystemExit(f"Forbidden source-level layout/top-matter manipulation: {found_forbidden}")

    artifact_bibliography = ARTIFACT / "data" / "references.bib"
    if not artifact_bibliography.is_file():
        raise SystemExit("Missing artifact/data/references.bib; build from the complete project packet.")
    bibliography_match = (ROOT / "references.bib").read_bytes() == artifact_bibliography.read_bytes()
    if not bibliography_match:
        raise SystemExit("Paper and artifact bibliography snapshots differ.")

    source_dir = (Path(results) if results is not None else ARTIFACT / "results") / "tex"
    source = source_dir / "corpus_counts.tex"
    if not source.is_file():
        raise SystemExit("Run artifact/scripts/reproduce.py before building the paper.")
    generated = ROOT / "generated"
    if generated.is_symlink() or generated.resolve() != ROOT.resolve() / "generated":
        raise SystemExit("The generated-fragment directory must remain inside this paper.")
    generated.mkdir(exist_ok=True)
    for fragment in sorted(source_dir.glob("*.tex")):
        shutil.copyfile(fragment, generated / fragment.name)

    citation = subprocess.run([sys.executable, "check_citations.py"], cwd=ROOT, env=env, check=False)
    if citation.returncode:
        raise SystemExit("Bibliography/citation audit failed; inspect bibliography-audit.json.")

    build = ROOT / "build"
    if build.is_symlink() or build.resolve() != ROOT.resolve() / "build":
        raise SystemExit("The build directory must remain inside this paper.")
    build.mkdir(exist_ok=True)

    latex = [
        pdflatex,
        "-no-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build",
        "main.tex",
    ]
    commands = [latex, [bib, "build/main"], latex, latex, latex]
    records = []
    for i, cmd in enumerate(commands, 1):
        output = build / f"command-{i}.txt"
        code, record = run(cmd, cwd=ROOT, env=env, out_path=output)
        text = output.read_text(encoding="utf-8", errors="replace")
        record["accepted_bibliography_warnings"] = False
        records.append(record)
        if code:
            raise SystemExit(f"Build command {i} failed; inspect paper/build/command-{i}.txt.")

    pdf = build / "main.pdf"
    log = (build / "main.log").read_text(encoding="utf-8", errors="replace")
    fatal_patterns = {
        "overfull_boxes": "Overfull \\hbox",
        "overfull_vboxes": "Overfull \\vbox",
        "undefined_references": "There were undefined references",
        "undefined_citations": "Citation `",
        "undefined_control_sequence": "Undefined control sequence",
    }
    findings = {name: log.count(pattern) for name, pattern in fatal_patterns.items()}
    if any(findings.values()):
        raise SystemExit(f"LaTeX preflight failed: {findings}")

    info = subprocess.run([pdfinfo, str(pdf)], text=True, encoding="utf-8", errors="replace",
                          capture_output=True, check=True).stdout
    info_map = {}
    for line in info.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info_map[key.strip()] = value.strip()
    pages = int(info_map.get("Pages", "0"))
    if not 0 < pages <= MAX_PAGES:
        raise SystemExit(f"Expected at most {MAX_PAGES} pages in the local review budget; built {pages}.")

    qpdf_status = "not_available"
    qpdf = shutil.which("qpdf")
    if qpdf:
        check = subprocess.run([qpdf, "--check", str(pdf)], text=True, capture_output=True, check=False)
        qpdf_status = "passed" if check.returncode == 0 else "failed"
        (build / "qpdf-check.txt").write_text(check.stdout + check.stderr, encoding="utf-8")
        if check.returncode:
            raise SystemExit("qpdf structural check failed; inspect paper/build/qpdf-check.txt.")

    bib_output = (build / "command-2.txt").read_text(encoding="utf-8", errors="replace")
    bib_warnings = [line for line in bib_output.splitlines() if line.startswith("Warning--")]
    warning_note = (
        "No BibTeX warnings were emitted.\n"
        if not bib_warnings
        else "BibTeX warnings are fatal under this build contract.\n"
    )
    (ROOT / "bibliography-warnings.txt").write_text(
        f"BibTeX metadata warnings: {len(bib_warnings)}\n"
        + warning_note
        + ("\n".join(bib_warnings) + "\n" if bib_warnings else ""),
        encoding="utf-8",
    )
    if bib_warnings:
        raise SystemExit("BibTeX emitted warnings; inspect paper/bibliography-warnings.txt.")
    citation_report = json.loads((ROOT / "bibliography-audit.json").read_text(encoding="utf-8"))
    evidence = {
        "status": "passed",
        "pdf": "build/main.pdf",
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "source_sha256": source_binding(ROOT),
        "log_sha256": hashlib.sha256((build / "main.log").read_bytes()).hexdigest(),
        "local_page_budget": MAX_PAGES,
        "pages": pages,
        "page_size": info_map.get("Page size"),
        "file_size_bytes": pdf.stat().st_size,
        "commands": records,
        "latex_findings": findings,
        "bibliography_warning_count": len(bib_warnings),
        "citation_audit": citation_report,
        "artifact_bibliography_match": bibliography_match,
        "template_contract": {
            "documentclass": "manuscript,screen,review",
            "forbidden_source_patterns_found": found_forbidden,
            "source_contract_passed": True,
        },
        "qpdf_check": qpdf_status,
        "visual_inspection": "separate manual page-image inspection required",
    }
    (ROOT / "build-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Built {pdf}: {pages} pages; {citation_report['unique_cited_entries']} cited works.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, help="External reproduction output directory (containing tex/).")
    main(parser.parse_args().results)
