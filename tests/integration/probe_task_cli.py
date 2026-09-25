"""Independent black-box contract, not tests supplied by the development Agent."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def probe(root):
    with tempfile.TemporaryDirectory(prefix='framework-contract-') as d:
        database = Path(d) / 'tasks.json'
        def command(*args, success=True):
            result = subprocess.run([sys.executable, '-B', '-m', 'taskcli', '--db', str(database), *args],
                                    cwd=root, text=True, capture_output=True, timeout=15)
            assert (result.returncode == 0) == success, (args, result.returncode, result.stderr)
            return json.loads(result.stdout) if success else None
        assert command('list') == []
        assert not database.exists(), 'list created a missing database'
        assert command('add', '  first  ') == {'id': 1, 'title': 'first', 'done': False}
        assert command('add', 'second') == {'id': 2, 'title': 'second', 'done': False}
        assert command('done', '1') == {'id': 1, 'title': 'first', 'done': True}
        assert command('list') == [{'id': 1, 'title': 'first', 'done': True}, {'id': 2, 'title': 'second', 'done': False}]
        before = database.read_bytes()
        command('add', ' ', success=False)
        command('done', '999', success=False)
        assert database.read_bytes() == before, 'invalid operation changed data'
        database.write_text('malformed database')
        command('list', success=False)
        assert database.read_text() == 'malformed database'
    print('CONTRACT_PASS: missing-db, add, monotonic IDs, list, done, invalid title/id/db preservation')


if __name__ == '__main__':
    try:
        probe(Path(sys.argv[1]).resolve())
    except (AssertionError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print('CONTRACT_FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
