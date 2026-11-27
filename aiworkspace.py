#!/usr/bin/env python3
"""Create and check a local, file-based workspace for AI-assisted projects."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import integrations

VERSION = "0.2.0"
TEMPLATES = Path(__file__).resolve().parent / "templates"
DIRECTORIES = ("00 Inbox", "10 Projects", "20 Library", "30 Templates", "90 Archive", "99 System")
PROJECT_FILES = ("PROJECT.md", "TASKS.md", "HANDOFF.md")
GITHUB_URL = re.compile(r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", re.ASCII)
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


def project_slug(slug):
    if len(slug) > 63 or not SLUG.fullmatch(slug):
        raise ValueError("Use a project slug such as podcast-site, up to 63 characters.")
    return slug


def github_url(value):
    if not GITHUB_URL.fullmatch(value) or value.rsplit("/", 1)[1] in (".", "..", ".git"):
        raise ValueError("Use a GitHub HTTPS repository URL without credentials, query, or fragment.")
    return value


def projects_directory(root):
    require_directory(root)
    require_file(root / "AGENTS.md")
    projects = root / "10 Projects"
    require_directory(projects)
    return projects


def new_project(root, slug, github=None):
    project_slug(slug)
    projects = projects_directory(root)
    if github is not None:
        github_url(github)
    texts = {name: template(name).replace("{{project}}", slug) for name in PROJECT_FILES}
    if github:
        texts["REPOSITORY"] = github + "\n"
        texts["PROJECT.md"] += "\n## Code repository\n\n" + github + "\n"
    project = projects / slug
    project.mkdir()
    for name, value in texts.items():
        with (project / name).open("x", encoding="utf-8") as handle:
            handle.write(value)
    print(f"Project created: {project}")


def repository_url(project):
    link = project / "REPOSITORY"
    require_file(link)
    return github_url(link.read_text(encoding="utf-8").strip())


def clone_project(root, slug, destination):
    project = projects_directory(root) / project_slug(slug)
    require_directory(project)
    url = repository_url(project)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Clone destination must be new: {destination}")
    require_directory(destination.parent)
    if destination.resolve().is_relative_to(root.resolve()):
        raise ValueError("Keep Git clones outside the synced workspace.")
    subprocess.run(["git", "clone", "--", url, str(destination)], check=True)
    print(f"Repository cloned: {destination}")


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
        link = project / "REPOSITORY"
        if link.exists() or link.is_symlink():
            repository_url(project)
        count += 1
    print(f"Workspace layout is valid ({count} project(s)).")


def doctor(root, workspace_parent, require_git=False):
    failures = []
    if root is not None:
        try:
            check(root)
        except (OSError, ValueError) as error:
            failures.append(str(error))
    if workspace_parent is not None:
        try:
            require_directory(workspace_parent)
            print(f"Workspace parent available: {workspace_parent}")
        except ValueError as error:
            failures.append(str(error))
    git = shutil.which("git")
    print("Git available." if git else "Git unavailable. Install Git before using GitHub.")
    if require_git and not git:
        failures.append("Git is required for this setup.")
    if failures:
        raise ValueError(" ".join(failures))


def setup(root, slug, github=None, destination=None):
    project_slug(slug)
    if github is not None:
        github_url(github)
    require_directory(root.parent)
    existing_checkout = False
    if destination is not None:
        if github is None:
            raise ValueError("--checkout requires --github.")
        if not shutil.which("git"):
            raise ValueError("Install Git before using --checkout.")
        require_directory(destination.parent)
        if destination.resolve().is_relative_to(root.resolve()):
            raise ValueError("Keep Git clones outside the synced workspace.")
        if destination.exists() or destination.is_symlink():
            require_directory(destination)
            checkout = subprocess.run(
                ["git", "-C", str(destination), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True,
            )
            remote = subprocess.run(
                ["git", "-C", str(destination), "config", "--local", "--get-all", "remote.origin.url"],
                capture_output=True, text=True,
            )
            if (checkout.returncode or Path(checkout.stdout.strip()).resolve() != destination.resolve()
                    or remote.returncode or remote.stdout.splitlines() != [github]):
                raise ValueError("Existing checkout must be a Git root with the expected origin.")
            existing_checkout = True
    if not root.is_symlink() and (not root.exists() or (root.is_dir() and not any(root.iterdir()))):
        init(root)
    check(root)
    project = projects_directory(root) / slug
    if not project.exists():
        new_project(root, slug, github)
    elif github is not None and repository_url(project) != github:
        raise ValueError("Project already links to a different GitHub repository.")
    if destination is not None:
        if existing_checkout:
            print(f"Existing checkout verified: {destination}")
        else:
            clone_project(root, slug, destination)
    check(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("init", "initialize a new or empty folder"),
        ("new", "create a project without replacing any existing files"),
        ("check", "check the workspace layout without writing"),
        ("clone", "clone the linked GitHub repository outside the workspace"),
    ):
        cli = sub.add_parser(command, help=help_text)
        cli.add_argument("root", type=Path)
        if command in ("new", "clone"):
            cli.add_argument("slug")
        if command == "new":
            cli.add_argument("--github", help="link an HTTPS GitHub repository")
        if command == "clone":
            cli.add_argument("destination", type=Path)
    cli = sub.add_parser("doctor", help="diagnose local setup without writing")
    cli.add_argument("--root", type=Path)
    cli.add_argument("--workspace-parent", type=Path)
    cli.add_argument("--require-git", action="store_true")
    cli = sub.add_parser("setup", help="initialize a workspace and create or reuse one project")
    cli.add_argument("root", type=Path)
    cli.add_argument("slug")
    cli.add_argument("--github")
    cli.add_argument("--checkout", type=Path, help="clone or verify the Git checkout outside the workspace")
    cli = sub.add_parser("docs-read", help="read a Google Doc and its current revision")
    cli.add_argument("document_id")
    cli = sub.add_parser("docs-append", help="append stdin to a Google Doc with a revision guard")
    cli.add_argument("document_id")
    cli.add_argument("--revision", required=True)
    cli = sub.add_parser("pr-status", help="report a GitHub PR head and its CI checks")
    cli.add_argument("repository", help="owner/repository")
    cli.add_argument("number", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "docs-read":
            print(json.dumps(integrations.document_snapshot(args.document_id), ensure_ascii=False))
            return 0
        if args.command == "docs-append":
            print(json.dumps(integrations.append_document(args.document_id, args.revision, sys.stdin.read())))
            return 0
        if args.command == "pr-status":
            if args.number < 1 or not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", args.repository):
                raise ValueError("Use owner/repository and a positive PR number.")
            github_url("https://github.com/" + args.repository)
            print(json.dumps(integrations.pull_request_report(args.repository, args.number), indent=2))
            return 0
        if args.command == "doctor":
            doctor(args.root.expanduser() if args.root else None,
                   args.workspace_parent.expanduser() if args.workspace_parent else None,
                   args.require_git)
            return 0
        root = args.root.expanduser()
        if args.command == "setup":
            setup(root, args.slug, args.github, args.checkout.expanduser() if args.checkout else None)
            return 0
        if args.command == "init":
            init(root)
        elif args.command == "new":
            new_project(root, args.slug, args.github)
        elif args.command == "clone":
            clone_project(root, args.slug, args.destination.expanduser())
        else:
            check(root)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"AIWorkspace: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
