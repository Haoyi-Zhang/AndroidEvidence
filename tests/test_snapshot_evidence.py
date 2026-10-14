"""Benign evidence-mutation and optimization-mode regressions."""

import copy
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from snapshot_evidence import source_count_macros, validate_snapshot_evidence


ART = Path(__file__).resolve().parents[1]


def current_fixture():
    source = {'main.tex': 's' * 64}
    pdf_hash, log_hash = 'p' * 64, 'l' * 64
    build = {
        'status': 'passed', 'pdf': 'build/main.pdf', 'pages': 39,
        'local_page_budget': 39, 'source_sha256': source,
        'pdf_sha256': pdf_hash, 'log_sha256': log_hash,
    }
    visual = {
        'status': 'PASS', 'pdf': 'build/main.pdf', 'page_count': 39,
        'local_page_budget': 39, 'source_sha256': source,
        'pdf_sha256': pdf_hash, 'log_sha256': log_hash,
        'full_size_pages_inspected': list(range(1, 40)),
        'required_parent_pages': list(range(1, 40)),
        'pending_parent_all_page_inspection': False,
        'render_dpi': 108, 'font_embedding': 'all listed fonts embedded',
        'scope': 'Layout only; not independent peer review.',
        'comparison_to_primary': {
            'byte_identical_to_current_primary': True,
            'byte_identical_to_receipt_selected_pdf': True,
            'receipt_selected_pdf_sha256': pdf_hash,
            'primary_pdf': '../../paper/build/main.pdf',
        },
    }
    result_build = copy.deepcopy(build)
    result_build['pdf'] = 'manuscript_snapshot/build/main.pdf'
    result_visual = copy.deepcopy(visual)
    result_visual['pdf'] = 'manuscript_snapshot/build/main.pdf'
    result_visual['comparison_to_primary']['primary_pdf'] = '../paper/build/main.pdf'
    return {
        'build': build, 'visual': visual,
        'result_build': result_build, 'result_visual': result_visual,
        'budget': 39, 'source_sha256': source,
        'pdf_sha256': pdf_hash, 'log_sha256': log_hash,
        'checked': 88, 'unchecked': 9,
        'macro_counts': {'snapshot generated': (88, 9),
                         'default build input': (88, 9)},
        'primary': {
            'build': copy.deepcopy(build), 'source_sha256': source,
            'pdf_sha256': pdf_hash, 'log_sha256': log_hash, 'budget': 39,
        },
    }


class SnapshotEvidenceRegressions(unittest.TestCase):
    def test_consistent_current_fixture_passes(self):
        validate_snapshot_evidence(**current_fixture())

    def test_stale_36_page_fixture_rejected(self):
        case = current_fixture()
        for record in (case['build'], case['result_build']):
            record['pages'] = 36
            record['local_page_budget'] = 36
        for record in (case['visual'], case['result_visual']):
            record['page_count'] = 36
            record['local_page_budget'] = 36
            record['full_size_pages_inspected'] = list(range(1, 37))
            record['required_parent_pages'] = list(range(1, 37))
        case['budget'] = 36
        with self.assertRaisesRegex(ValueError, 'current primary paper'):
            validate_snapshot_evidence(**case)

    def test_stale_source_and_default_count_rejected(self):
        stale = current_fixture()
        stale['build']['source_sha256'] = {'main.tex': 'o' * 64}
        stale['result_build']['source_sha256'] = {'main.tex': 'o' * 64}
        stale['visual']['source_sha256'] = {'main.tex': 'o' * 64}
        stale['result_visual']['source_sha256'] = {'main.tex': 'o' * 64}
        with self.assertRaisesRegex(ValueError, 'active inputs'):
            validate_snapshot_evidence(**stale)
        stale = current_fixture()
        stale['macro_counts']['default build input'] = (87, 10)
        with self.assertRaisesRegex(ValueError, 'default build input'):
            validate_snapshot_evidence(**stale)

    def test_altered_log_visual_and_mirror_rejected(self):
        case = current_fixture()
        case['log_sha256'] = 'x' * 64
        with self.assertRaisesRegex(ValueError, 'actual final log'):
            validate_snapshot_evidence(**case)
        case = current_fixture()
        for record in (case['visual'], case['result_visual']):
            record['full_size_pages_inspected'].pop()
        with self.assertRaisesRegex(ValueError, 'every snapshot page'):
            validate_snapshot_evidence(**case)
        case = current_fixture()
        case['result_visual']['render_dpi'] = 72
        with self.assertRaisesRegex(ValueError, 'result visual mirror'):
            validate_snapshot_evidence(**case)

    def test_source_count_parser_rejects_partial_or_duplicate_definitions(self):
        self.assertEqual((88, 9), source_count_macros(
            r'\newcommand{\SourceCheckedWorks}{88}'
            r'\newcommand{\SourceUncheckedWorks}{9}'))
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            source_count_macros(r'\newcommand{\SourceCheckedWorks}{88}')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            source_count_macros(r'\newcommand{\SourceCheckedWorks}{88}' * 2)


class QualityGateOptimizationRegressions(unittest.TestCase):
    def _run_gate(self, *, sections, extra='', optimized=False, binding_defect=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scripts = root / 'artifact/scripts'
            manuscript = root / 'artifact/manuscript_snapshot'
            scripts.mkdir(parents=True)
            manuscript.mkdir(parents=True)
            shutil.copyfile(ART / 'scripts/manuscript_quality_gate.py',
                            scripts / 'manuscript_quality_gate.py')
            shutil.copyfile(ART / 'manuscript_snapshot/build.py', manuscript / 'build.py')
            abstract = ' '.join(['Android lineage evidence requires explicit assumptions.'] * 25)
            main = (r'\documentclass[manuscript,screen,review]{acmart}' + '\n'
                    + r'\begin{abstract}' + abstract + r'\end{abstract}' + '\n'
                    + 'Research question 1. ' + extra + '\n'
                    + ''.join(r'\section{Section ' + str(n) + '}' + '\n'
                              for n in range(sections)))
            (manuscript / 'main.tex').write_text(main, encoding='utf-8')
            for name in ('references.bib', 'acmart.cls', 'ACM-Reference-Format.bst'):
                (manuscript / name).write_text('', encoding='utf-8')
            build = manuscript / 'build'
            build.mkdir()
            (build / 'main.log').write_text('Clean final fixture log.\n', encoding='utf-8')
            (build / 'main.pdf').write_bytes(b'benign local PDF fixture')
            config = runpy.run_path(str(manuscript / 'build.py'))
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            evidence = {
                'status': 'passed', 'source_sha256': config['source_binding'](manuscript),
                'pdf_sha256': digest(build / 'main.pdf'),
                'log_sha256': digest(build / 'main.log'), 'pages': 1,
            }
            (manuscript / 'build-evidence.json').write_text(
                json.dumps(evidence), encoding='utf-8')
            if binding_defect == 'source':
                (manuscript / 'main.tex').write_text(main + '% changed fixture source\n',
                                                    encoding='utf-8')
            elif binding_defect == 'pdf':
                (build / 'main.pdf').write_bytes(b'changed benign local PDF fixture')
            elif binding_defect == 'log':
                (build / 'main.log').write_text('Changed clean final fixture log.\n',
                                                encoding='utf-8')
            command = [sys.executable]
            if optimized:
                command.append('-O')
            command += [str(scripts / 'manuscript_quality_gate.py'), '--snapshot',
                        '--out', str(root / 'gate-result.json')]
            return subprocess.run(command, capture_output=True, text=True, timeout=10)

    def test_h1_ceiling_and_prose_guard_fail_with_and_without_optimization(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized, defect='H1'):
                result = self._run_gate(sections=10, optimized=optimized)
                self.assertNotEqual(0, result.returncode)
                self.assertIn('Expected 7-9 H1 sections', result.stderr)
            with self.subTest(optimized=optimized, defect='prose'):
                result = self._run_gate(sections=8, extra='current checkpoint',
                                        optimized=optimized)
                self.assertNotEqual(0, result.returncode)
                self.assertIn('Unfinished-state phrase', result.stderr)

    def test_current_source_pdf_log_binding_rejects_mutation_in_both_modes(self):
        messages = {
            'source': 'Build evidence does not bind the active manuscript source',
            'pdf': 'PDF differs from the current build binding',
            'log': 'Final LaTeX log differs from the current build binding',
        }
        for optimized in (False, True):
            for defect, message in messages.items():
                with self.subTest(optimized=optimized, defect=defect):
                    result = self._run_gate(sections=8, optimized=optimized,
                                            binding_defect=defect)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn(message, result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
