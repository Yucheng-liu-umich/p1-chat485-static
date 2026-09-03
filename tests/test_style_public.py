"""Check Python style with ruff.

EECS 485 Project 1
"""

import subprocess

import utils


def test_ruff_check():
    """Run ruff check."""
    # No inline suppressions allowed: refactor the code instead of silencing
    # the linter.
    assert_no_prohibited_terms(
        "noqa", targets=("chat485generator", "tests/test_student.py")
    )
    subprocess.run(
        [
            "ruff",
            "check",
            "--config",
            str(utils.TEST_DIR / "testdata/ruff.toml"),
            "chat485generator",
            "tests/test_student.py",
        ],
        check=True,
    )


def test_ruff_format():
    """Run ruff format --check."""
    # No formatter inline suppressions allowed: refactor the code instead of
    # silencing the formatter.
    assert_no_prohibited_terms(
        "fmt: skip",
        "fmt: off",
        "fmt: on",
        targets=("chat485generator", "tests/test_student.py"),
    )
    subprocess.run(
        [
            "ruff",
            "format",
            "--check",
            "--config",
            str(utils.TEST_DIR / "testdata/ruff.toml"),
            "chat485generator",
            "tests/test_student.py",
        ],
        check=True,
    )


def assert_no_prohibited_terms(*terms, allow=(), targets=("chat485generator",)):
    """Check for prohibited terms before testing style.

    Each `term` is searched for as a literal substring in `targets` (source
    files under chat485generator by default).  Lines containing any substring
    listed in `allow` are exempt -- use this to carve out narrow, documented
    exceptions.
    """
    for term in terms:
        completed_process = subprocess.run(
            [
                "grep",
                "-r",
                "-n",
                term,
                "--include=*.py",
                "--exclude=__init__.py",
                *targets,
            ],
            check=False,  # We filter the output ourselves below.
            stdout=subprocess.PIPE,
            text=True,
        )

        # Drop any line that matches an allowed-exception substring.  When
        # `allow` is empty (the common case) this is just splitlines().
        bad_lines = [
            line
            for line in completed_process.stdout.splitlines()
            if not any(allowed in line for allowed in allow)
        ]

        assert not bad_lines, f"The term '{term}' is prohibited.\n" + "\n".join(
            bad_lines
        )
