# Google Docs and GitHub checks

These commands are optional. The bootstrap and Drive desktop workflow still work without API credentials.

## Native Google Docs

Enable Google Docs API in your Google Cloud project. Obtain a short-lived user OAuth access token in your own environment, using the Docs scope and an account that can edit the test document. For example, an approved Desktop OAuth client can be used with Google Cloud CLI:

```bash
gcloud auth application-default login \
  --client-id-file="/path/outside/workspace/client.json" \
  --scopes="https://www.googleapis.com/auth/documents"
```

Use a disposable document with a single tab and text-only paragraphs. The Docs scope can apply to other documents your account can edit, so only use it where your authorization allows. Keep credentials outside the workspace. Assign the token without printing it or adding it to the command history:

```bash
export AIWORKSPACE_GOOGLE_ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
python3 aiworkspace.py docs-read DOCUMENT_ID
```

The output includes the document text and an opaque revision. Use protected local output or a test document. Copy only the revision into the next command:

```bash
printf '%s\n' 'Next action: review the draft.' |
  python3 aiworkspace.py docs-append DOCUMENT_ID --revision REVISION_FROM_READ
unset AIWORKSPACE_GOOGLE_ACCESS_TOKEN
```

The append requires the same revision at the server and verifies the resulting text by reading it back. If the revision changed, reread before deciding what to append. If a write succeeded and readback cannot confirm it, inspect the document before retrying. Tables, inline objects, and multiple tabs are outside this initial command. The CLI does not change sharing or create OAuth permissions.

## GitHub pull request status

Authenticate GitHub CLI with an account allowed to read the repository. Then run:

```bash
gh auth status
python3 aiworkspace.py pr-status owner/repository 42
```

The report includes the head SHA, draft and mergeability fields, and the checks returned for that PR by GitHub CLI. Empty checks mean no checks were reported. To inspect a different head, read the PR again and compare SHA values. The command does not start, rerun, merge, or close anything.
