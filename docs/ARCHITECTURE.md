# Architecture

The workspace is a document tree. It can live locally or under Google Drive for desktop. Source code stays in a separate Git clone. The CLI uses local file operations and the installed Git client.

| Layer | Responsibility |
| --- | --- |
| Workspace rules | Tell an assistant where to begin and what access is required |
| Project brief and task list | Record the goal, inputs, owner, decisions, and acceptance evidence |
| Handoff | Records the last verified state and the next action |
| Repository link | A `REPOSITORY` file holds one HTTPS GitHub URL without credentials |
| Bootstrap CLI | Creates the tree, links repositories, clones them, and checks the layout |
| API adapters | Google Docs reads and guarded append use the Docs API. GitHub status uses a read-only GitHub CLI command. |
| External tools | Drive for desktop syncs files. Git and GitHub handle branches, PRs, and code history |

The CLI refuses to initialize a nonempty folder or clone inside the workspace. Authentication stays with Git, GitHub, or Google Drive. The layout check validates local files and URL format. Drive sync and access to a remote repository are verified separately during the walkthrough.

Use a scoped workspace folder and a non-sensitive sample when connecting an assistant. Project files are the handoff between assistants and the place to record which code changes they are discussing.
