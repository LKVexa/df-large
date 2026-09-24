"""Build and exercise a disposable payload copy; leave release evidence sealed."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = next((ROOT / 'vm').iterdir())


def run(args, cwd, env=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=600, env=env)
    output = result.stdout + result.stderr
    print(' '.join(map(str, args)))
    print(output[-16000:])
    if result.returncode:
        raise SystemExit(result.returncode)


def main():
    with tempfile.TemporaryDirectory(prefix='df-large-native-') as temp:
        copy = Path(temp) / 'repository'
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.build', '_runs', '__pycache__'))
        vm = copy / 'vm' / PAYLOAD.name
        run(['make'], vm)
        run(['make', 'brctl-dev', 'size'], vm)
        run(['make', 'sanitize'], vm)
        executable = vm / '.build/host_io_regressions'
        run(['cc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
             '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-DBR_DEVELOPMENT=1',
             '-Isrc', '-Iadapters', 'src/brvm.c', 'src/brtrust.c', 'adapters/br_file_adapter.c',
             str(copy / 'tests/test_host_io.c'), '-o', str(executable), '-lcrypto'], vm)
        run([str(executable)], vm, {**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
