# AIWorkspace

AIWorkspace keeps project context in files so the work can continue across AI assistants, chats, and devices.

An AI assistant can draft a result in one chat and another can pick it up from the project files. The project description says what matters, the task list records the outcome and evidence, and the handoff tells the next assistant where to start.

## Quick start

Requires Python 3.9 or later. No dependencies, accounts, or network calls are needed for the local pilot.

```bash
python3 aiworkspace.py init "$HOME/AIWorkspace-pilot"
python3 aiworkspace.py new "$HOME/AIWorkspace-pilot" demo
python3 aiworkspace.py check "$HOME/AIWorkspace-pilot"
```

Open the new project's `PROJECT.md`, `TASKS.md`, and `HANDOFF.md`. Follow the [two-chat walkthrough](docs/QUICKSTART.md) to complete a sample task.

## What is in v0.1

- A local initializer and layout check.
- English project, task, handoff, and assistant instructions.
- A small experiment you can run with an assistant you already use.

The local starter is the release boundary. Drive sync, GitHub coordination, voice mirrors, scheduled jobs, and site deployment require separate integration and are outside this version.

[Architecture](docs/ARCHITECTURE.md) · [Release notes](CHANGELOG.md)
