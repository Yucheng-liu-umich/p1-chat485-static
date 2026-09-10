"""Student test suite for chat485generator CLI edge cases and functionality."""

import json
import subprocess


def run_cli(args):
    """Execute chat485generator CLI with provided arguments."""
    return subprocess.run(
        ["chat485generator"] + args,
        capture_output=True,
        text=True,
        check=False,
    )


def test_output_dir_already_exists(tmp_path):
    """Test error when specified output directory already exists."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "templates").mkdir()
    (input_dir / "config.json").write_text("[]", encoding="utf-8")

    out_dir = tmp_path / "existing_output"
    out_dir.mkdir()
    sentinel = out_dir / "keep_me.txt"
    sentinel.write_text("safe", encoding="utf-8")

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "already exists" in res.stdout
    assert str(out_dir) in res.stdout
    assert sentinel.exists()
    assert sentinel.read_text(encoding="utf-8") == "safe"


def test_missing_config_file(tmp_path):
    """Test error when config.json is missing in input directory."""
    input_dir = tmp_path / "empty_input"
    input_dir.mkdir()
    (input_dir / "templates").mkdir()
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "config.json" in res.stdout
    assert "not found" in res.stdout
    assert not out_dir.exists()


def test_invalid_json_config(tmp_path):
    """Test error when config.json contains malformed JSON."""
    input_dir = tmp_path / "invalid_json_input"
    input_dir.mkdir()
    (input_dir / "templates").mkdir()
    (input_dir / "config.json").write_text("{ invalid json }", encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "config.json" in res.stdout


def test_missing_templates_directory(tmp_path):
    """Test error when templates directory is completely missing."""
    input_dir = tmp_path / "no_templates_input"
    input_dir.mkdir()
    (input_dir / "config.json").write_text("[]", encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "templates" in res.stdout
    assert "not found" in res.stdout


def test_missing_template_file(tmp_path):
    """Test error when a specific template referenced in config is missing."""
    input_dir = tmp_path / "missing_template_input"
    input_dir.mkdir()
    (input_dir / "templates").mkdir()

    config_data = [{"url": "/", "template": "nonexistent.html", "context": {}}]
    (input_dir / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "nonexistent.html" in res.stdout


def test_invalid_jinja_syntax(tmp_path):
    """Test error when template file contains unclosed Jinja tags."""
    input_dir = tmp_path / "bad_syntax_input"
    input_dir.mkdir()
    tmpl_dir = input_dir / "templates"
    tmpl_dir.mkdir()

    (tmpl_dir / "broken.html").write_text(
        "<h1>{% if True %}No Endif</h1>", encoding="utf-8"
    )
    config_data = [{"url": "/", "template": "broken.html", "context": {}}]
    (input_dir / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode != 0
    assert "chat485generator error:" in res.stdout
    assert "broken.html" in res.stdout


def test_multiple_pages_and_nested_urls(tmp_path):
    """Test rendering multiple pages with nested directory structures."""
    input_dir = tmp_path / "multi_page_input"
    input_dir.mkdir()
    tmpl_dir = input_dir / "templates"
    tmpl_dir.mkdir()

    (tmpl_dir / "main.html").write_text("<h1>{{ title }}</h1>", encoding="utf-8")

    config_data = [
        {"url": "/", "template": "main.html", "context": {"title": "Home"}},
        (
            {
                "url": "/nested/deep/page/",
                "template": "main.html",
                "context": {"title": "Deep Page"},
            }
        ),
    ]
    (input_dir / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode == 0

    index_file = out_dir / "index.html"
    nested_file = out_dir / "nested" / "deep" / "page" / "index.html"

    assert index_file.exists()
    assert "<h1>Home</h1>" in index_file.read_text(encoding="utf-8")

    assert nested_file.exists()
    assert "<h1>Deep Page</h1>" in nested_file.read_text(encoding="utf-8")


def test_autoescape_enabled(tmp_path):
    """Test that Jinja autoescape converts HTML characters to safe entities."""
    input_dir = tmp_path / "autoescape_input"
    input_dir.mkdir()
    tmpl_dir = input_dir / "templates"
    tmpl_dir.mkdir()

    (tmpl_dir / "esc.html").write_text("<div>{{ content }}</div>", encoding="utf-8")
    config_data = [
        {
            "url": "/",
            "template": "esc.html",
            "context": {"content": "<script>alert('xss')</script>"},
        }
    ]
    (input_dir / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode == 0

    rendered = (out_dir / "index.html").read_text(encoding="utf-8")
    assert "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in rendered
    assert "<script>" not in rendered


def test_static_directory_copy_location(tmp_path):
    """Test that static files are copied directly into output root directory."""
    input_dir = tmp_path / "static_input"
    input_dir.mkdir()
    (input_dir / "templates").mkdir()
    (input_dir / "config.json").write_text("[]", encoding="utf-8")

    static_dir = input_dir / "static"
    css_dir = static_dir / "css"
    css_dir.mkdir(parents=True)
    (css_dir / "style.css").write_text("body { color: red; }", encoding="utf-8")

    out_dir = tmp_path / "output"

    res = run_cli([str(input_dir), "-o", str(out_dir)])
    assert res.returncode == 0

    copied_css = out_dir / "css" / "style.css"
    wrong_static_path = out_dir / "static"

    assert copied_css.exists()
    assert copied_css.read_text(encoding="utf-8") == "body { color: red; }"
    assert not wrong_static_path.exists()


def test_verbose_flag_output(tmp_path):
    """Test stdout messages with and without -v/--verbose option."""
    input_dir = tmp_path / "verbose_input"
    input_dir.mkdir()
    tmpl_dir = input_dir / "templates"
    tmpl_dir.mkdir()

    (tmpl_dir / "dummy.html").write_text("ok", encoding="utf-8")
    config_data = [{"url": "/", "template": "dummy.html", "context": {}}]
    (input_dir / "config.json").write_text(json.dumps(config_data), encoding="utf-8")

    static_dir = input_dir / "static"
    static_dir.mkdir()
    (static_dir / "file.txt").write_text("data", encoding="utf-8")

    # Non-verbose run
    out_dir1 = tmp_path / "out1"
    res1 = run_cli([str(input_dir), "-o", str(out_dir1)])
    assert res1.returncode == 0
    assert "Rendered" not in res1.stdout
    assert "Copied" not in res1.stdout

    # Verbose run
    out_dir2 = tmp_path / "out2"
    res2 = run_cli([str(input_dir), "-o", str(out_dir2), "-v"])
    assert res2.returncode == 0
    assert "Rendered dummy.html ->" in res2.stdout
    assert "Copied" in res2.stdout
