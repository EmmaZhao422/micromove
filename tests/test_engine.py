import concurrent.futures
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/micromove.py'
spec = importlib.util.spec_from_file_location('engine', SCRIPT)
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

class EngineTest(unittest.TestCase):
    def setUp(self):
        self.s = {**e.DEFAULT, 'enabled': True}
        self.now = datetime(2026, 9, 25, 11, 0, tzinfo=timezone.utc)

    def test_daily_slots_deduplicate_and_reset_next_day(self):
        self.assertTrue(e.due(self.s, self.now))
        self.assertFalse(e.due(self.s, self.now))
        self.assertTrue(e.due(self.s, self.now.replace(hour=16)))
        self.assertTrue(e.due(self.s, self.now + timedelta(days=1)))

    def test_no_catchup_after_window(self):
        self.assertFalse(e.due(self.s, self.now.replace(minute=30)))
        self.assertFalse(e.due(self.s, self.now.replace(hour=10)))

    def test_pause_wins_over_snooze(self):
        self.s.update(enabled=False, snooze_until=self.now.timestamp()-1)
        self.assertFalse(e.due(self.s, self.now))

    def test_snooze_has_priority_and_no_double_delivery(self):
        self.s['snooze_until'] = (self.now + timedelta(minutes=10)).timestamp()
        self.assertFalse(e.due(self.s, self.now))
        self.assertTrue(e.due(self.s, self.now + timedelta(minutes=10)))
        self.assertFalse(e.due(self.s, self.now + timedelta(minutes=11)))

    def test_invalid_urls_and_times(self):
        for value in ('javascript:alert(1)', 'https://user:pass@example.com', 'http://example.com'):
            with self.assertRaises(Exception): e.web_url(value)
        for value in ('25:00', '9:00', '-1'):
            with self.assertRaises(Exception): e.clock_time(value)

    def test_hook_fails_open_without_retaining_transcript(self):
        with tempfile.TemporaryDirectory() as d:
            env={**os.environ, 'MICROMOVE_DATA_DIR': d}
            for raw in ('not json', '[]', '{"hook_event_name":"Stop","stop_hook_active":true}'):
                p=subprocess.run([sys.executable,str(SCRIPT),'hook'],input=raw,text=True,encoding="utf-8",capture_output=True,env=env)
                self.assertEqual(p.returncode,0)
                self.assertEqual(json.loads(p.stdout),{})
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_cli_lifecycle_and_state_outside_repository(self):
        with tempfile.TemporaryDirectory() as d:
            env={**os.environ,'MICROMOVE_DATA_DIR':d}
            def cli(*args):
                p=subprocess.run([sys.executable,str(SCRIPT),*args],capture_output=True,text=True,encoding="utf-8",env=env)
                self.assertEqual(p.returncode,0,p.stderr)
                return json.loads(p.stdout)
            self.assertFalse(cli('status')['enabled'])
            self.assertTrue(cli('enable')['enabled'])
            cli('configure','--url','https://example.com','--times','11:00','16:00')
            self.assertEqual(cli('start')['url'],'https://example.com')
            self.assertGreater(cli('snooze','10')['snooze_until'],0)
            self.assertEqual(cli('done')['snooze_until'],0)
            self.assertFalse(cli('pause')['enabled'])

    def test_real_hook_process_emits_one_nonblocking_message(self):
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, 'MICROMOVE_DATA_DIR': d}
            def cli(*args, raw=None):
                return subprocess.run([sys.executable, str(SCRIPT), *args],
                                      input=raw, capture_output=True, text=True,encoding="utf-8", env=env)
            self.assertEqual(cli('enable').returncode, 0)
            self.assertEqual(cli('configure', '--times', datetime.now().strftime('%H:%M')).returncode, 0)
            raw = json.dumps({'hook_event_name': 'Stop', 'last_assistant_message': 'PRIVATE_TEST_MARKER'})
            first = cli('hook', raw=raw)
            self.assertEqual(first.returncode, 0)
            self.assertEqual(set(json.loads(first.stdout)), {'systemMessage'})
            self.assertEqual(json.loads(cli('hook', raw=raw).stdout), {})
            for file in Path(d).iterdir():
                self.assertNotIn(b'PRIVATE_TEST_MARKER', file.read_bytes())

    def test_utf8_output_under_legacy_windows_encoding(self):
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, 'MICROMOVE_DATA_DIR': d, 'PYTHONIOENCODING': 'cp1252'}
            result = subprocess.run([sys.executable, str(SCRIPT), 'demo'],
                                    capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout.decode('utf-8'))['message'], e.MESSAGE)
            invalid = subprocess.run([sys.executable, str(SCRIPT), 'snooze', '0'],
                                     capture_output=True, env=env)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn('分钟数', invalid.stderr.decode('utf-8'))

    def test_install_probe_and_doctor_do_not_consume_reminder(self):
        with tempfile.TemporaryDirectory(prefix='微习惯 test ') as d:
            env = {**os.environ, 'MICROMOVE_DATA_DIR': d}
            def cli(*args, raw=None):
                p = subprocess.run([sys.executable, str(SCRIPT), *args], input=raw,
                                   capture_output=True, text=True, encoding='utf-8', env=env)
                self.assertEqual(p.returncode, 0, p.stderr)
                return json.loads(p.stdout)
            report = cli('doctor')
            self.assertIsNone(report['last_hook'])
            self.assertEqual(report['host_trust'], 'unknown')
            self.assertFalse(report['enabled'])
            cli('enable')
            cli('configure', '--times', datetime.now().strftime('%H:%M'))
            cli('probe')
            raw = json.dumps({'hook_event_name': 'Stop', 'last_assistant_message': 'PRIVATE_PROBE_MARKER'})
            self.assertIn('安装检查', cli('hook', raw=raw)['systemMessage'])
            report = cli('doctor')
            self.assertFalse(report['probe_pending'])
            self.assertEqual(report['last_hook']['event'], 'Stop')
            self.assertEqual(report['ui_delivery'], 'unverified')
            self.assertIn(e.MESSAGE, cli('hook', raw=raw)['systemMessage'])
            self.assertEqual(cli('hook', raw=raw), {})
            cli('probe')
            cli('pause')
            self.assertEqual(cli('hook', raw=raw), {})
            for file in Path(d).iterdir():
                self.assertNotIn(b'PRIVATE_PROBE_MARKER', file.read_bytes())

    def test_concurrent_checks_deliver_once(self):
        with tempfile.TemporaryDirectory() as d:
            old=os.environ.get('MICROMOVE_DATA_DIR')
            os.environ['MICROMOVE_DATA_DIR']=d
            try:
                with e.state() as s: s['enabled']=True
                def check(_):
                    with e.state() as s: return e.due(s,self.now)
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                    self.assertEqual(sum(pool.map(check,range(16))),1)
            finally:
                if old is None: os.environ.pop('MICROMOVE_DATA_DIR')
                else: os.environ['MICROMOVE_DATA_DIR']=old

if __name__ == '__main__': unittest.main()
