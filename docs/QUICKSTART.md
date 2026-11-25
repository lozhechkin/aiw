# Your first task across Drive, GitHub, and two chats

## Prepare your accounts

1. Sign in to Google Drive for desktop. In Finder or Explorer, locate an accessible folder under My Drive. Use a new child folder as the workspace root. Make the pilot folder available offline if your setup streams files and your assistant needs local access. The examples use Bash. On Windows, use Git Bash or translate the commands to PowerShell.
2. Create a small test repository on GitHub with a README. Use a private repository if the test might contain personal data. For a private repository, make sure Git can authenticate with your configured credential helper or with `gh auth login` and `gh auth setup-git`. Avoid putting credentials in URLs or project files.
3. Run the README commands. Confirm that `PROJECT.md` and `HANDOFF.md` appear in Drive and that `git -C "$checkout" remote get-url origin` gives the intended repository. A successful local check does not measure sync or remote permissions.

## Open a change in GitHub

From the clone, create a branch and add a small non-sensitive test file. Run this block once in a fresh clone and review the diff before committing.

```bash
cd "$checkout"
git switch -c pilot/first-task
printf '%s\n' 'AIWorkspace handoff pilot' > pilot-note.txt
git diff --no-index -- /dev/null pilot-note.txt
```

Once reviewed, commit and push that branch:

```bash
git add pilot-note.txt
git commit -m "Add handoff pilot note"
git push -u origin pilot/first-task
```

Open a pull request in GitHub. With an authenticated GitHub CLI you can instead run:

```bash
gh pr create --title "Test the AIWorkspace handoff" --body "A non-sensitive pilot change."
```

Keep the PR open for the second chat to review.

## Pass the work between chats

Open `10 Projects/demo` in Drive or from the synced folder. Give the first assistant the workspace `AGENTS.md`, the project's three Markdown files, and the PR URL. Ask it to record these in `HANDOFF.md`: the PR URL, last verified commit SHA, what the PR changes, and one open review question. If the assistant only receives attachments, save its output to Drive yourself.

Open another chat. Give it the same project folder and authorized access to the PR or an exported diff. Ask it to identify the offered change and report one check it can perform. The pilot passes when the new chat can name the PR, the expected version, and the open question from the files, without a recap of the first chat.

If Drive shows old content, wait for sync and compare the handoff in both clients. If the assistant cannot read the PR, use the authorized GitHub connection or provide the non-sensitive diff as an attachment.
