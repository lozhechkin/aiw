"""Opt-in Google Docs and GitHub operations using existing credentials."""

import json
import os
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

DOCS_API = "https://docs.googleapis.com/v1/documents/"
DOC_ID = re.compile(r"[a-zA-Z0-9_-]{1,200}", re.ASCII)
PR_FIELDS = "number,url,state,isDraft,mergeable,headRefOid,statusCheckRollup"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def docs_request(doc_id, suffix, payload=None):
    if not DOC_ID.fullmatch(doc_id):
        raise ValueError("Supply a Google Docs document ID.")
    token = os.environ.get("AIWORKSPACE_GOOGLE_ACCESS_TOKEN", "")
    if not token or any(c.isspace() for c in token):
        raise ValueError("Set AIWORKSPACE_GOOGLE_ACCESS_TOKEN to a short-lived Google access token.")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(DOCS_API + doc_id + suffix, data=data, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    })
    try:
        with build_opener(NoRedirect()).open(request, timeout=25) as response:
            return json.load(response)
    except HTTPError as error:
        action = "write" if payload is not None else "read"
        raise ValueError(f"Google Docs {action} returned HTTP {error.code}. Check access and revision.") from None
    except (URLError, OSError, ValueError):
        if payload is not None:
            raise ValueError("Google Docs write outcome is unknown. Re-read before retrying.") from None
        raise ValueError("Google Docs read request or response failed.") from None


def document_snapshot(doc_id):
    document = docs_request(doc_id, "?includeTabsContent=true")
    try:
        tabs = document["tabs"]
        if len(tabs) != 1 or tabs[0].get("childTabs"):
            raise ValueError("Only documents with one tab are supported.")
        tab = tabs[0]
        tab_id = tab["tabProperties"]["tabId"]
        content = tab["documentTab"]["body"]["content"]
        texts = []
        for block in content:
            if "sectionBreak" in block:
                continue
            for part in block["paragraph"]["elements"]:
                texts.append(part["textRun"]["content"])
        revision = document["revisionId"]
        if not revision or not tab_id or not texts or not texts[-1].endswith("\n"):
            raise ValueError("Google Docs did not return a usable revision and text body.")
        return {"revision": revision, "tab_id": tab_id, "text": "".join(texts)}
    except (KeyError, IndexError, TypeError):
        raise ValueError("The document must have one tab, a readable revision, and text-only paragraphs.") from None


def append_document(doc_id, revision, text):
    if not text.strip() or any(
        (ord(c) < 32 and c not in "\n\t") or 0xE000 <= ord(c) <= 0xF8FF for c in text
    ):
        raise ValueError("Append non-empty plain text without unsupported control characters.")
    before = document_snapshot(doc_id)
    if revision != before["revision"]:
        raise ValueError("Google Docs revision changed. Read it again before appending.")
    addition = "\n" + text.rstrip("\n")
    docs_request(doc_id, ":batchUpdate", {
        "writeControl": {"requiredRevisionId": revision},
        "requests": [{"insertText": {
            "endOfSegmentLocation": {"tabId": before["tab_id"]},
            "text": addition,
        }}],
    })
    try:
        after = document_snapshot(doc_id)
    except ValueError as error:
        raise ValueError(f"Append was accepted but readback failed. Re-read before retrying. {error}") from None
    if after["tab_id"] != before["tab_id"] or after["text"] != before["text"][:-1] + addition + "\n":
        raise ValueError("Append was accepted but readback differs. Re-read before retrying.")
    return {"revision": after["revision"], "verified": True}


def pull_request_report(repository, number):
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(number), "--repo", "github.com/" + repository, "--json", PR_FIELDS],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("GitHub CLI is unavailable or timed out.") from None
    if result.returncode:
        raise ValueError("GitHub CLI could not read the PR. Check gh auth status and repository access.")
    try:
        report = json.loads(result.stdout)
        if not re.fullmatch(r"[0-9a-f]{40}", report["headRefOid"]):
            raise ValueError()
        if report["number"] != number or not isinstance(report["statusCheckRollup"], (list, type(None))):
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        raise ValueError("GitHub did not return the requested PR and its head SHA.") from None
    report["checksReported"] = bool(report["statusCheckRollup"])
    return report
