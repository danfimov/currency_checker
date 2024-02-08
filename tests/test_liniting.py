import subprocess
import warnings

import pytest


def run_linter(name: str, cmd: list[str], warn_only: bool = False) -> None:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True
    )

    msgs = []
    out, err = process.communicate()
    if process.returncode != 0:

        if err:
            msgs.append('{} exited with code {} and has unexpected output on stderr:\n{}'
                        .format(name, process.returncode, err.decode().rstrip()))
        if out:
            msgs.append('{} found issues:\n{}'.format(name, out.decode().rstrip()))
        if not msgs:
            msgs.append('{} exited with code {} and has no output on stdout or stderr.'
                        .format(name, process.returncode))
        if warn_only:
            warnings.warn('\n'.join(msgs))
        else:
            pytest.fail('\n'.join(msgs))


@pytest.mark.linting
def test_ruff() -> None:
    cmd = ['python', '-m', 'ruff', 'currency_checker', 'tests']
    run_linter('ruff', cmd)


@pytest.mark.linting
def test_mypy() -> None:
    cmd = ['python', '-m', 'mypy', 'currency_checker']
    run_linter('mypy', cmd)
