"""P1 autograder utility functions."""

import json
import shutil
import subprocess
from pathlib import Path

# Directory containing unit tests
TEST_DIR = Path(__file__).parent

# Directory containing unit test input files
TESTDATA_DIR = TEST_DIR / "testdata"


def assert_valid_html(root):
    """Validate every HTML file under `root` against the HTML5 W3C spec.

    Runs `html5validator`, which bundles the Nu Html Checker (`vnu`) and needs
    a Java runtime.  It is a declared dependency in requirements.txt, so a
    missing validator means a broken environment and fails rather than skips.

    `--ignore JAVA_TOOL_OPTIONS` drops the spurious "Picked up
    JAVA_TOOL_OPTIONS" line some JREs print to stderr, which the validator
    would otherwise read as a validation error.
    """
    assert shutil.which("html5validator"), (
        "html5validator not found.  It is in requirements.txt; "
        "activate your virtual environment and ensure a Java runtime is "
        "available."
    )
    result = subprocess.run(
        ["html5validator", "--root", str(root), "--ignore", "JAVA_TOOL_OPTIONS"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"HTML validation failed:\n{result.stdout + result.stderr}"
    )


def assert_config_not_modified(input_dir):
    """Raise an assertion if the seed Chat485 data was removed or changed.

    Students may *add* conversations as a reach goal, so this is a subset
    check, not an exact-equality check.  Every seed page in the original config
    must still be present, with the same template and the same context, except
    that a page's `conversations` sidebar list may gain extra entries as long as
    it still contains every seed conversation.  Adding brand-new page entries
    (a student's own conversation) is allowed; removing or editing seed pages,
    seed messages, or seed conversations is not.
    """
    input_dir = Path(input_dir)
    assert str(input_dir) == input_dir.name, "Expected a basename"
    original_config_path = (TESTDATA_DIR / input_dir / "config.json").resolve()
    student_config_path = (input_dir / "config.json").resolve()
    assert student_config_path != original_config_path
    with student_config_path.open(encoding="utf-8") as infile:
        student_config = json.load(infile)
    with original_config_path.open(encoding="utf-8") as infile:
        original_config = json.load(infile)

    student_by_url = {entry["url"]: entry for entry in student_config}
    for original_entry in original_config:
        url = original_entry["url"]
        assert url in student_by_url, (
            f"Seed page '{url}' is missing from {input_dir}/config.json"
        )
        student_entry = student_by_url[url]
        assert student_entry["template"] == original_entry["template"], (
            f"Seed page '{url}' template was modified"
        )
        _assert_context_preserved(
            original_entry["context"], student_entry.get("context", {}), url
        )


def _assert_context_preserved(original_context, student_context, url):
    """Assert every seed context value survives, allowing extra conversations.

    The `conversations` sidebar list is checked as a subset (seed conversations
    must remain, extras are welcome); every other key must match exactly.
    """
    for key, original_value in original_context.items():
        assert key in student_context, f"Seed key '{key}' missing from '{url}' context"
        if key == "conversations":
            for conversation in original_value:
                assert conversation in student_context[key], (
                    f"Seed conversation {conversation} missing from "
                    f"the sidebar on '{url}'"
                )
        else:
            assert student_context[key] == original_value, (
                f"Seed value for '{key}' on '{url}' was modified"
            )
