"""Validate generated HTML against the HTML5 W3C spec.

EECS 485 Project 1
"""

import subprocess
from pathlib import Path

import utils

HELLO_WORLD_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
ANN_ARBOR_UUID = "c3d4e5f6-a7b8-9012-cdef-123456789012"


def test_html(tmpdir):
    """Validate generated HTML5 in chat485_html/.

    Note: 'tmpdir' is a fixture provided by the pytest package.  It creates a
    unique temporary directory before the test runs, and removes it afterward.
    https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture

    """
    utils.assert_config_not_modified("chat485")
    outdir = tmpdir / "chat485_html"
    subprocess.run(
        ["chat485generator", "chat485", "-o", outdir],
        check=True,
    )

    # Verify expected files are present
    assert Path(outdir / "index.html").exists()
    assert Path(outdir / f"conversations/{HELLO_WORLD_UUID}/index.html").exists()
    assert Path(outdir / f"conversations/{ANN_ARBOR_UUID}/index.html").exists()

    # Verify HTML5
    utils.assert_valid_html(outdir)
