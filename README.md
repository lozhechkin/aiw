# AIWorkspace

AIWorkspace keeps project context in files so work can continue across AI assistants, chats, and devices. In this release, project documents can sync through Google Drive and code stays in a separate GitHub repository. The project folder contains the link between them.

## Quick start with Drive and GitHub

Clone this repository and run the commands from its root. You need Python 3.9+, Git, a locally accessible folder managed by Google Drive for desktop, and access to a GitHub repository. Use a repository with an initial commit, such as a test repository initialized with a README.

Replace the three example values before running these commands. The workspace folder and the clone destination should be new, with existing parent directories. Choose a clone destination outside all synced folders.

```bash
workspace="$HOME/path/to/synced-drive/AIWorkspace"
repository="https://github.com/your-account/demo"
checkout="$HOME/Projects/demo"

mkdir -p "$HOME/Projects"
python3 aiworkspace.py doctor --workspace-parent "$(dirname "$workspace")" --require-git
python3 aiworkspace.py setup "$workspace" demo --github "$repository" --checkout "$checkout"
python3 aiworkspace.py check "$workspace"
```

Open the workspace in Drive to verify synchronization. Then follow the [Drive and GitHub walkthrough](docs/QUICKSTART.md) to create a test change and continue it in a second chat.

## What AIWorkspace does

- Creates a workspace and English project, task, handoff, and assistant instructions.
- Links a project to a GitHub repository and clones it outside the workspace.
- Uses Drive for desktop for file sync and your existing Git credentials for GitHub.
- Checks the local layout and the format of saved repository URLs without writing.
- Optionally reads a native Google Doc, appends text with a revision guard and readback, and reports a GitHub PR head and CI checks.

Drive synchronization is managed by Google Drive for desktop. GitHub pull requests are opened in GitHub or with your authenticated GitHub CLI. See [integrations](docs/INTEGRATIONS.md) for optional native Docs and PR reporting. Scheduled automation and richer integrations are described in the [roadmap](docs/ROADMAP.md).

A local-only pilot remains available. Choose a local root and omit `--github` and `--checkout`. Rerunning `setup` preserves existing project files and checks their repository link. With `--checkout`, it reuses an existing checkout only when its Git root and original origin URL match. You can also run `doctor --root <workspace>` to diagnose an existing layout.

[Architecture](docs/ARCHITECTURE.md) · [Release notes](CHANGELOG.md)

Released under the [MIT License](LICENSE), covering the code, documentation, and templates in this release.
