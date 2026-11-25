#!/usr/bin/env python3
"""Create and check a local, file-based workspace for AI-assisted projects."""

import argparse
from pathlib import Path
import re
import sys

VERSION = "0.1.0"
TEMPLATES = Path(__file__).resolve().parent / "templates"
DIRECTORIES = ("00 Inbox", "10 Projects", "20 Library", "30 Templates", "90 Archive", "99 System")
PROJECT_FILES = ("PROJECT.md", "TASKS.md", "HANDOFF.md")
SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", re.ASCII)


def template(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")


def require_directory(path):
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"Expected a real directory: {path}")


def require_file(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def init(root):
    agent_rules = template("AGENTS.md")
    if root.is_symlink():
        raise ValueError(f"Workspace root cannot be a symlink: {root}")
    root.mkdir(exist_ok=True)
    if any(root.iterdir()):
        raise ValueError(f"Workspace root must be empty: {root}")
    for name in DIRECTORIES:
        (root / name).mkdir()
    with (root / "AGENTS.md").open("x", encoding="utf-8") as handle:
        handle.write(agent_rules)
    print(f"Workspace created: {root}")


def new_project(root, slug):
    if len(slug) > 63 or not SLUG.fullmatch(slug):
        raise ValueError("Use a project slug such as podcast-site, up to 63 characters.")
    require_directory(root)
    require_file(root / "AGENTS.md")
    projects = root / "10 Projects"
    require_directory(projects)
    texts = {name: template(name).replace("{{project}}", slug) for name in PROJECT_FILES}
    project = projects / slug
    project.mkdir()
    for name, value in texts.items():
        with (project / name).open("x", encoding="utf-8") as handle:
            handle.write(value)
    print(f"Project created: {project}")


def check(root):
    require_directory(root)
    require_file(root / "AGENTS.md")
    for name in DIRECTORIES:
        require_directory(root / name)
    count = 0
    for project in sorted((root / "10 Projects").iterdir()):
        if project.name.startswith(".") and not project.is_dir() and not project.is_symlink():
            continue
        require_directory(project)
        for name in PROJECT_FILES:
            require_file(project / name)
        count += 1
    print(f"Workspace layout is valid ({count} project(s)).")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("init", "initialize a new or empty folder"),
        ("new", "create a project without replacing any existing files"),
        ("check", "check the workspace layout without writing"),
    ):
        cli = sub.add_parser(command, help=help_text)
        cli.add_argument("root", type=Path)
        if command == "new":
            cli.add_argument("slug")
    args = parser.parse_args(argv)
    root = args.root.expanduser()
    try:
        if args.command == "init":
            init(root)
        elif args.command == "new":
            new_project(root, args.slug)
        else:
            check(root)
    except (OSError, ValueError) as error:
        print(f"AIWorkspace: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
