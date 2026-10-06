"""Narrow regressions for portable measurements and explicit coding boundaries."""
from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import resource_usage
import reproduce
from corpus_audit import nonindependent_status


class ReproductionControls(unittest.TestCase):
    def test_runner_counts_completed_summary_not_interleaved_progress(self):
        stderr = 'test_control ... owned checker failed as expected\nok\nRan 55 tests in 1.0s\n\nOK\n'
        self.assertEqual(reproduce.completed_test_count(stderr), 55)
        for incomplete in ('test_control ... ok\n', 'Ran 55 tests in 1.0s\nFAILED\n',
                           'Ran 55 tests in 1.0s\nOK (skipped=1)\n'):
            with self.assertRaises(ValueError):
                reproduce.completed_test_count(incomplete)

    def test_unavailable_measurements_are_null(self):
        with patch.object(resource_usage, 'resource', None):
            for children in (False, True):
                self.assertIsNone(resource_usage.usage(children)['cpu_seconds'])
                self.assertIsNone(resource_usage.usage(children)['peak_rss_kib'])

    def test_explicit_single_extractor_is_not_independent(self):
        self.assertTrue(nonindependent_status('source_grounded_coding; single_extractor'))
        self.assertTrue(nonindependent_status('source_recheck_2026_09_15_not_independent'))

    def test_missing_or_contradictory_boundary_is_rejected(self):
        for value in ('source_grounded_coding', 'independent',
                      'single_extractor; independent=true', 'single_extractor; dual_coding'):
            self.assertFalse(nonindependent_status(value))

    def test_linux_resource_units_and_children_selector(self):
        measured = SimpleNamespace(ru_utime=1.25, ru_stime=0.75, ru_maxrss=4096)
        fake = SimpleNamespace(RUSAGE_SELF=0, RUSAGE_CHILDREN=-1,
                               getrusage=lambda selector: measured if selector == -1 else None)
        with patch.object(resource_usage, 'resource', fake), \
             patch.object(resource_usage.sys, 'platform', 'linux'):
            result = resource_usage.usage(children=True)
            self.assertEqual(result['cpu_seconds'], 2.0)
            self.assertEqual(result['peak_rss_kib'], 4096)

    def test_darwin_rss_bytes_are_converted_to_kib(self):
        measured = SimpleNamespace(ru_utime=1.0, ru_stime=0.0, ru_maxrss=4096)
        fake = SimpleNamespace(RUSAGE_SELF=0, RUSAGE_CHILDREN=-1,
                               getrusage=lambda selector: measured)
        with patch.object(resource_usage, 'resource', fake), \
             patch.object(resource_usage.sys, 'platform', 'darwin'):
            self.assertEqual(resource_usage.usage()['peak_rss_kib'], 4)

    def test_runner_retains_failure_and_stops_before_later_checks(self):
        with TemporaryDirectory() as folder, \
             patch.object(sys, 'argv', ['reproduce.py', '--out', folder]), \
             patch.object(reproduce.subprocess, 'run', return_value=SimpleNamespace(returncode=1)) as run:
            self.assertEqual(reproduce.main(), 1)
            self.assertEqual(run.call_count, 1)
            report = json.loads((Path(folder) / 'reproduction/run.json').read_text())
            self.assertEqual(report['status'], 'incomplete_or_failed')
            self.assertEqual(report['commands'][0]['exit_code'], 1)

    def test_runner_records_timeout_without_promoting_results(self):
        timeout = reproduce.subprocess.TimeoutExpired(['owned checker'], 45)
        with TemporaryDirectory() as folder, \
             patch.object(sys, 'argv', ['reproduce.py', '--out', folder]), \
             patch.object(reproduce.subprocess, 'run', side_effect=timeout) as run:
            self.assertEqual(reproduce.main(), 1)
            self.assertEqual(run.call_count, 1)
            report = json.loads((Path(folder) / 'reproduction/run.json').read_text())
            self.assertTrue(report['commands'][0]['timed_out'])
            self.assertEqual(report['status'], 'incomplete_or_failed')
            self.assertIn('exceeded', (Path(folder) / 'reproduction/corpus.stderr.txt').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
