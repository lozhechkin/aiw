# Architecture

A workspace is a folder. The built-in commands work on local files and leave model selection, sharing, and automation to the owner.

| Layer | Responsibility |
| --- | --- |
| Workspace rules | Tell an assistant what to read, where it may work, and when it needs permission |
| Project brief | Describes the goal, authoritative inputs, decisions, and limits |
| Task list | Gives an owner, outcome, evidence, and next action |
| Handoff | Records the last verified state for the next chat |
| Bootstrap CLI | Copies the English templates into an empty workspace and checks the layout |

The CLI refuses to initialize a nonempty folder or overwrite a project. A layout check confirms the expected files and directories. It cannot establish that their content is accurate or that an assistant actually has access.

Keep the release and your workspace in separate directories. You can put a project under version control or use a synced folder after choosing who can access it. Integrate one service at a time and verify reading and writing with a non-sensitive example before relying on it.
