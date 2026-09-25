"""Bounded subprocesses; no shell interpolation or background ownership leaks."""
import os
import signal
import subprocess
import tempfile
import time


def run(argv, cwd, timeout, env, stdin=''):
    child_env = dict(os.environ, **env)
    child_env['PYTHONDONTWRITEBYTECODE'] = '1'
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err, tempfile.TemporaryFile() as inp:
        inp.write(stdin.encode())
        inp.seek(0)
        try:
            proc = subprocess.Popen(argv, cwd=str(cwd), env=child_env, stdin=inp,
                                    stdout=out, stderr=err, start_new_session=True)
        except FileNotFoundError:
            return {'exit_code': 127, 'stdout': '', 'stderr': 'DEPENDENCY_MISSING: ' + argv[0], 'timed_out': False}
        timed_out, limit = False, False
        started = time.monotonic()
        try:
            while proc.poll() is None:
                timed_out = time.monotonic() - started > timeout
                limit = out.tell() + err.tell() > 4 * 1024 * 1024
                if timed_out or limit:
                    os.killpg(proc.pid, signal.SIGKILL)
                    break
                time.sleep(0.03)
            proc.wait()
        except BaseException:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            raise
        out.seek(0)
        err.seek(0)
        return {'exit_code': proc.returncode, 'stdout': out.read(4 * 1024 * 1024).decode(errors='replace'),
                'stderr': err.read(1024 * 1024).decode(errors='replace'),
                'timed_out': timed_out, 'output_limit': limit}
