"""Validate handcoded HTML against the HTML5 W3C spec.

EECS 485 Project 1
"""

from pathlib import Path

import utils

CONVERSATION_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def test_html():
    """Validate handcoded HTML5 in handcoded_html/."""
    assert Path("handcoded_html/index.html").exists()
    assert Path(f"handcoded_html/conversations/{CONVERSATION_UUID}/index.html").exists()
    utils.assert_valid_html("handcoded_html")
