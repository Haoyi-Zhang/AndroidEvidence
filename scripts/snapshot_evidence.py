"""Snapshot-record checks and a read-only PDF page-count consumer."""

import re
import shutil
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _comparable(record, omitted):
    return {key: value for key, value in record.items() if key not in omitted}


def pdf_page_count(path):
    """Read the selected PDF's actual count; never infer it from a receipt."""
    info = subprocess.check_output(
        [shutil.which('pdfinfo') or 'pdfinfo', str(path)], text=True,
        encoding='utf-8', errors='replace', timeout=30)
    match = re.search(r'^Pages:\s+(\d+)\s*$', info, re.M)
    require(match is not None, 'pdfinfo did not report an actual PDF page count')
    return int(match.group(1))


def source_count_macros(text):
    """Return displayed checked/unchecked counts, or None if no fallback exists."""
    values = []
    for name in ('SourceCheckedWorks', 'SourceUncheckedWorks'):
        matches = re.findall(r'\\newcommand\s*\{\\' + name + r'\}\s*\{(\d+)\}', text)
        require(len(matches) <= 1, f'Duplicate {name} definition')
        values.append(int(matches[0]) if matches else None)
    require(values[0] is None and values[1] is None or
            values[0] is not None and values[1] is not None,
            'Incomplete SourceCheckedWorks/SourceUncheckedWorks definitions')
    return tuple(values) if values[0] is not None else None


def validate_snapshot_evidence(*, build, visual, result_build, result_visual,
                               budget, source_sha256, pdf_sha256, log_sha256,
                               checked, unchecked, macro_counts, actual_pages,
                               primary=None):
    """Reject stale or cross-version evidence; no PDF, TeX, or network work occurs here.

    ``primary`` is absent in an artifact-only checkout. When present it contains
    the sibling paper's build evidence, active source binding, PDF/log digests,
    and configured page budget.
    """
    require(build.get('status') == 'passed', 'Snapshot build did not pass')
    require(visual.get('status') == 'PASS', 'Snapshot visual review did not pass')
    require(build.get('pdf') == visual.get('pdf') == 'build/main.pdf',
            'Snapshot records select different PDFs')
    require(result_build.get('pdf') == result_visual.get('pdf') ==
            'manuscript_snapshot/build/main.pdf', 'Result mirrors select a different PDF')

    require(_comparable(build, {'pdf', 'pdf_path_basis', 'command_execution_root', 'scope'}) ==
            _comparable(result_build, {'pdf', 'pdf_path_basis', 'command_execution_root', 'scope'}),
            'Snapshot build and result build mirror differ')
    snapshot_visual = dict(visual)
    result_visual_copy = dict(result_visual)
    for record in (snapshot_visual, result_visual_copy):
        comparison = dict(record.get('comparison_to_primary', {}))
        comparison.pop('primary_pdf', None)
        record['comparison_to_primary'] = comparison
    require(_comparable(snapshot_visual, {'pdf', 'pdf_path_basis'}) ==
            _comparable(result_visual_copy, {'pdf', 'pdf_path_basis'}),
            'Snapshot visual and result visual mirror differ')

    require(isinstance(budget, int) and budget > 0, 'Invalid snapshot page budget')
    require(build.get('local_page_budget') == visual.get('local_page_budget') == budget,
            'Snapshot page budget differs from build.py')
    pages = build.get('pages')
    require(isinstance(pages, int) and 0 < pages <= budget, 'Snapshot page count exceeds budget')
    require(type(actual_pages) is int and actual_pages == pages,
            'Snapshot build page count differs from the actual PDF')
    require(visual.get('page_count') == pages, 'Snapshot visual page count differs from build')
    all_pages = list(range(1, pages + 1))
    if visual.get('coverage_kind') == 'pixel-identity-to-primary':
        require(build.get('primary_relation') is None,
                'Pixel-identity mirror coverage cannot describe a research excerpt')
        commands = build.get('commands', [])
        require(len(commands) == 5 and all(command.get('exit_code') == 0 for command in commands),
                'Full mirror lacks the five-command successful primary build record')
        viewed = visual.get('full_size_pages_inspected', [])
        require(viewed and viewed == sorted(set(viewed)) and
                all(type(page) is int and page in all_pages for page in viewed),
                'Actual full-size page views are missing or invalid')
        pixels = visual.get('pixel_identity_to_primary', {})
        require(pixels.get('primary_pdf_sha256') == pixels.get('snapshot_pdf_sha256') == pdf_sha256,
                'Pixel identity does not bind the actual byte-identical PDFs')
        rows = pixels.get('pages', [])
        require([row.get('page') for row in rows] == all_pages,
                'Pixel identity does not cover every snapshot page')
        for row in rows:
            require(type(row.get('width')) is int and row['width'] > 0 and
                    type(row.get('height')) is int and row['height'] > 0 and
                    re.fullmatch(r'[0-9a-f]{64}', row.get('primary_pixels_sha256', '')) and
                    row.get('primary_pixels_sha256') == row.get('snapshot_pixels_sha256'),
                    'Primary/snapshot rendered pixels differ or lack a complete binding')
        require(visual.get('comparison_to_primary', {}).get('byte_identical_to_current_primary') is True,
                'Pixel mirror must affirm actual primary byte identity')
    else:
        require(visual.get('full_size_pages_inspected') == all_pages,
                'Full-size visual inspection does not cover every snapshot page')
    require(visual.get('required_parent_pages') == all_pages,
            'Required visual pages do not cover every snapshot page')
    require(visual.get('pending_parent_all_page_inspection') is False,
            'All-page visual inspection remains pending')
    require(isinstance(visual.get('render_dpi'), (int, float)) and
            visual['render_dpi'] > 0, 'Visual render DPI is missing')
    require(visual.get('font_embedding') == 'all listed fonts embedded',
            'Font embedding evidence is missing')
    require('not independent peer review' in visual.get('scope', ''),
            'Visual scope boundary is missing')

    require(build.get('source_sha256') == visual.get('source_sha256') == source_sha256,
            'Snapshot source binding differs from active inputs')
    require(build.get('pdf_sha256') == visual.get('pdf_sha256') == pdf_sha256,
            'Snapshot PDF hash differs from actual PDF')
    require(build.get('log_sha256') == visual.get('log_sha256') == log_sha256,
            'Snapshot log hash differs from actual final log')
    comparison = visual.get('comparison_to_primary', {})
    require(comparison.get('byte_identical_to_receipt_selected_pdf') is True and
            comparison.get('receipt_selected_pdf_sha256') == pdf_sha256,
            'Visual receipt selects another PDF')

    require(isinstance(checked, int) and isinstance(unchecked, int) and
            checked >= 0 and unchecked >= 0, 'Invalid dynamic source counts')
    require(macro_counts, 'No SourceCheckedWorks count fragment was checked')
    for name, counts in macro_counts.items():
        require(counts == (checked, unchecked),
                f'{name} SourceCheckedWorks/SourceUncheckedWorks differs from current data')

    relation = build.get('primary_relation')
    if relation is not None:
        require(relation.get('kind') == 'research-content-excerpt',
                'Unknown snapshot relation to primary paper')
        exceptions = relation.get('source_exceptions', {})
        require(set(exceptions) == {'main.tex', 'sections/02-method.tex'},
                'Excerpt changes unexpected primary source inputs')
        for name, values in exceptions.items():
            require(values.get('snapshot') == source_sha256.get(name) and
                    values.get('primary') != values.get('snapshot'),
                    'Excerpt source exception does not bind active inputs')
        require(comparison.get('byte_identical_to_current_primary') is False and
                comparison.get('research_content_excerpt_of_current_primary') is True,
                'Excerpt must not claim primary PDF byte identity')

    if primary is not None:
        primary_build = primary['build']
        require(primary_build.get('status') == 'passed', 'Primary paper build did not pass')
        require(primary_build.get('pages') == primary['actual_pages'],
                'Primary build page count differs from the actual PDF')
        require(primary_build.get('source_sha256') == primary['source_sha256'],
                'Primary paper build does not bind active source')
        require(primary_build.get('pdf_sha256') == primary['pdf_sha256'] and
                primary_build.get('log_sha256') == primary['log_sha256'],
                'Primary paper PDF/log differs from its build evidence')
        require(primary_build.get('local_page_budget') == primary['budget'] == budget,
                'Snapshot page count/budget differs from current primary paper')
        if relation is None:
            require(primary_build.get('pages') == pages,
                    'Snapshot page count/budget differs from current primary paper')
            require(source_sha256 == primary['source_sha256'] and
                    pdf_sha256 == primary['pdf_sha256'] and
                    log_sha256 == primary['log_sha256'],
                    'Snapshot source/PDF/log differs from current primary paper')
            require(comparison.get('byte_identical_to_current_primary') is True,
                    'Visual comparison does not affirm current primary byte identity')
            require(build.get('commands') == primary_build.get('commands'),
                    'Full mirror compiler-command provenance differs from the primary build')
        else:
            require(relation.get('primary_pdf_sha256') == primary['pdf_sha256'] and
                    relation.get('primary_log_sha256') == primary['log_sha256'] and
                    relation.get('primary_pages') == primary_build.get('pages') == pages + 1,
                    'Excerpt differs from bound current primary paper')
            require(set(source_sha256) == set(primary['source_sha256']),
                    'Excerpt source input set differs from current primary paper')
            for name, digest in source_sha256.items():
                expected = relation['source_exceptions'].get(name)
                if expected is None:
                    require(digest == primary['source_sha256'][name],
                            'Excerpt changes an unlisted scientific input')
                else:
                    require(expected['primary'] == primary['source_sha256'][name],
                            'Excerpt exception differs from current primary source')
