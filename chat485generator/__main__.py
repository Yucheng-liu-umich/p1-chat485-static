"""Build static HTML site from directory of HTML templates and plain files."""

import json
import pathlib
import shutil
import sys

import click
import jinja2


def render_pages(template_env, config_data, output_path, verbose):
    """Render all pages defined in configuration."""
    for entry in config_data:
        url = entry.get("url", "")
        template_name = entry.get("template", "")
        context = entry.get("context", {})

        url_clean = url.lstrip("/")
        target_file = output_path / url_clean / "index.html"

        try:
            template = template_env.get_template(template_name)
            rendered_content = template.render(**context)
        except jinja2.TemplateError as err:
            print(f"chat485generator error: '{template_name}'\n{err}")
            sys.exit(1)

        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(rendered_content)
        except OSError as err:
            print(f"chat485generator error: Failed to write '{target_file}'\n{err}")
            sys.exit(1)

        if verbose:
            print(f"Rendered {template_name} -> {target_file}")


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(),
    default="generated_html",
    help="Output directory.",
)
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def main(input_dir, output_dir, verbose):
    """Templated static website generator."""
    input_path = pathlib.Path(input_dir)
    output_path = pathlib.Path(output_dir)

    if output_path.exists():
        print(f"chat485generator error: '{output_dir}' already exists")
        sys.exit(1)

    config_file = input_path / "config.json"
    template_dir = input_path / "templates"

    if not config_file.exists():
        print(f"chat485generator error: '{config_file}' not found")
        sys.exit(1)

    try:
        with open(config_file, encoding="utf-8") as f:
            config_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as err:
        print(f"chat485generator error: '{config_file}'\n{err}")
        sys.exit(1)

    template_path = template_dir if template_dir.is_dir() else input_path

    try:
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
    except jinja2.TemplateError as err:
        print(f"chat485generator error: Jinja configuration error\n{err}")
        sys.exit(1)

    render_pages(template_env, config_data, output_path, verbose)

    static_dir = input_path / "static"
    if static_dir.exists() and static_dir.is_dir():
        try:
            shutil.copytree(static_dir, output_path, dirs_exist_ok=True)
            if verbose:
                print(f"Copied {static_dir} -> {output_path}")
        except OSError as err:
            print(f"chat485generator error: Failed to copy static files\n{err}")
            sys.exit(1)


if __name__ == "__main__":
    main()
