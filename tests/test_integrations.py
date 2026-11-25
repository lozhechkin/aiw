import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import integrations


def document(text, revision):
    return {"revisionId": revision, "tabs": [{
        "tabProperties": {"tabId": "tab"},
        "documentTab": {"body": {"content": [
            {"paragraph": {"elements": [{"textRun": {"content": text}}]}},
        ]}},
    }]}


class DocsTests(unittest.TestCase):
    def test_append_uses_expected_revision_and_reads_back(self):
        with patch.object(integrations, "docs_request", side_effect=[
            document("before\n", "one"), {}, document("before\nновый текст\n", "two"),
        ]) as request:
            result = integrations.append_document("doc", "one", "новый текст\n")
        self.assertEqual(result, {"revision": "two", "verified": True})
        request.assert_any_call("doc", ":batchUpdate", {
            "writeControl": {"requiredRevisionId": "one"},
            "requests": [{"insertText": {
                "endOfSegmentLocation": {"tabId": "tab"}, "text": "\nновый текст",
            }}],
        })
        self.assertEqual(request.call_count, 3)

    def test_stale_revision_stops_before_mutation(self):
        with patch.object(integrations, "docs_request", return_value=document("before\n", "two")) as request:
            with self.assertRaisesRegex(ValueError, "revision changed"):
                integrations.append_document("doc", "one", "new")
        request.assert_called_once_with("doc", "?includeTabsContent=true")

    def test_readback_mismatch_is_reported(self):
        with patch.object(integrations, "docs_request", side_effect=[
            document("before\n", "one"), {}, document("unexpected\n", "two"),
        ]) as request:
            with self.assertRaisesRegex(ValueError, "readback differs"):
                integrations.append_document("doc", "one", "new")
        self.assertEqual(request.call_count, 3)

    def test_unsupported_tabs_fail_before_mutation(self):
        snapshot = document("before\n", "one")
        snapshot["tabs"].append({})
        with patch.object(integrations, "docs_request", return_value=snapshot) as request:
            with self.assertRaisesRegex(ValueError, "one tab"):
                integrations.append_document("doc", "one", "new")
        request.assert_called_once_with("doc", "?includeTabsContent=true")

    def test_invalid_document_id_stops_before_network(self):
        with patch.object(integrations, "build_opener") as opener:
            with self.assertRaisesRegex(ValueError, "document ID"):
                integrations.docs_request("../other", "")
        opener.assert_not_called()


class GitHubTests(unittest.TestCase):
    def test_report_keeps_exact_head_and_check_details(self):
        data = {"number": 42, "headRefOid": "a" * 40, "statusCheckRollup": [
            {"name": "tests", "conclusion": "SUCCESS", "detailsUrl": "https://github.com/example/test/actions/runs/1"},
        ]}
        with patch.object(integrations.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, json.dumps(data), "",
        )) as gh:
            report = integrations.pull_request_report("example/test", 42)
        self.assertEqual(report["headRefOid"], "a" * 40)
        self.assertEqual(report["statusCheckRollup"], data["statusCheckRollup"])
        self.assertTrue(report["checksReported"])
        self.assertEqual(gh.call_args.args[0][:5], ["gh", "pr", "view", "42", "--repo"])

    def test_empty_checks_are_not_reported_as_success(self):
        data = {"number": 42, "headRefOid": "a" * 40, "statusCheckRollup": []}
        with patch.object(integrations.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, json.dumps(data), "",
        )):
            self.assertFalse(integrations.pull_request_report("example/test", 42)["checksReported"])
