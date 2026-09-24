import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VM = next((ROOT / 'vm').iterdir())
spec = importlib.util.spec_from_file_location('audited_lctl430', VM / 'tools/lctl430.py')
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)


class SigningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / 'release.brimg'
        self.image.write_bytes(b'existing signed release')

    def compile(self, **kwargs):
        return compiler.compile_src(VM / 'src/BOOT.lctlc', self.image, True,
                                    self.root / 'manifest.json', self.root / 'brir.json', **kwargs)

    def assert_preserved(self):
        self.assertEqual(self.image.read_bytes(), b'existing signed release')
        self.assertFalse((self.root / 'manifest.json').exists())
        self.assertFalse((self.root / 'brir.json').exists())
        self.assertEqual(list(self.root.glob('.lctl-sign-*')), [])

    def test_missing_signer_does_not_publish_unsigned_output(self):
        with self.assertRaises(Exception):
            self.compile(sign_private='private.key')
        self.assert_preserved()

    def test_signer_failure_preserves_existing_release(self):
        with patch.object(compiler.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['signer'])):
            with self.assertRaises(subprocess.CalledProcessError):
                self.compile(sign_private='private.key', brctl='signer')
        self.assert_preserved()

    def test_signer_timeout_preserves_existing_release(self):
        with patch.object(compiler.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['signer'], 60)):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.compile(sign_private='private.key', brctl='signer')
        self.assert_preserved()

    def test_success_exit_with_unsigned_output_is_rejected(self):
        def unsigned_output(argv, **kwargs):
            Path(argv[3]).write_bytes(Path(argv[2]).read_bytes())
            return subprocess.CompletedProcess(argv, 0)
        with patch.object(compiler.subprocess, 'run', side_effect=unsigned_output):
            with self.assertRaises(Exception):
                self.compile(sign_private='private.key', brctl='signer')
        self.assert_preserved()

    def test_unsigned_compile_remains_deterministic(self):
        self.compile()
        first = self.image.read_bytes()
        self.compile()
        self.assertEqual(first, self.image.read_bytes())
        self.assertFalse(first[7] & 2)


if __name__ == '__main__':
    unittest.main()
