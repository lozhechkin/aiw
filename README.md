# AIWorkspace

AIWorkspace keeps project context in files so work can continue across AI assistants, chats, and devices. In v0.1, project documents can sync through Google Drive and code stays in a separate GitHub repository. The project folder contains the link between them.

## Quick start with Drive and GitHub

You need Python 3.9+, Git, a locally accessible folder managed by Google Drive for desktop, and access to a GitHub repository. Use a repository with an initial commit, such as a test repository initialized with a README.

Replace the three example values before running these commands. The workspace folder and the clone destination should be new, with existing parent directories. Choose a clone destination outside all synced folders.

```bash
workspace="$HOME/path/to/synced-drive/AIWorkspace"
repository="https://github.com/your-account/demo"
checkout="$HOME/Projects/demo"

mkdir -p "$HOME/Projects"
python3 aiworkspace.py init "$workspace"
python3 aiworkspace.py new "$workspace" demo --github "$repository"
python3 aiworkspace.py clone "$workspace" demo "$checkout"
python3 aiworkspace.py check "$workspace"
```

Open the workspace in Drive to verify synchronization. Then follow the [Drive and GitHub walkthrough](docs/QUICKSTART.md) to create a test change and continue it in a second chat.

## What v0.1 does

- Creates a workspace and English project, task, handoff, and assistant instructions.
- Links a project to a GitHub repository and clones it outside the workspace.
- Uses Drive for desktop for file sync and your existing Git credentials for GitHub.
- Checks the local layout and the format of saved repository URLs without writing.

Drive synchronization is managed by Google Drive for desktop. GitHub pull requests are opened in GitHub or with your authenticated GitHub CLI. Hosted Google Docs, provider connectors, and scheduled automation are described in the [roadmap](docs/ROADMAP.md).

A local-only pilot remains available. Choose a local root and omit `--github` and `clone`.

[Architecture](docs/ARCHITECTURE.md) · [Release notes](CHANGELOG.md)
