"""Callback contracts: correct outputs, clear errors, and no stale downloads."""

import unittest
from unittest.mock import patch

import app

ROW = [1, "Useful lesson", "Positive", 90.0, 10.0, "Check against the original text"]


class CallbackTests(unittest.TestCase):
    def test_success_returns_all_four_outputs(self):
        with patch("app.analyse_comments", return_value=[ROW]), patch("app.write_report", return_value="report.csv"):
            overview, table, report, status = app.run_dashboard("Useful lesson")
        self.assertIn("PREDICTED", overview.upper())
        self.assertEqual(table, [ROW])
        self.assertEqual(report, "report.csv")
        self.assertIn("complete", status)

    def test_invalid_input_clears_all_old_results(self):
        with patch("app.gr.Warning"):
            overview, table, report, status = app.run_dashboard(" \n ")
        self.assertEqual(overview, app.EMPTY)
        self.assertEqual(table, [])
        self.assertIsNone(report)
        self.assertIn("Paste", status)

    def test_model_failure_shows_friendly_message(self):
        with patch("app.analyse_comments", side_effect=RuntimeError("test failure")), patch("app.gr.Warning"), patch("app.logging.exception"):
            _, table, report, status = app.run_dashboard("A review")
        self.assertEqual(table, [])
        self.assertIsNone(report)
        self.assertIn("could not run", status)

    def test_token_html_escaping(self):
        with patch("app.inspect_tokens", return_value=([("<script>", 7)], 1)):
            markup, status = app.run_token_explorer("example")
        self.assertNotIn("<script>", markup)
        self.assertIn("&lt;script&gt;", markup)
        self.assertIn("1 tokens", status)

    def test_invalid_token_input(self):
        markup, message = app.run_token_explorer("first\nsecond")
        self.assertEqual(markup, "")
        self.assertIn("one comment", message)

    def test_load_and_clear_reset_results(self):
        sample = app.load_sample()
        cleared = app.clear_dashboard()
        self.assertEqual(len(sample), 5)
        self.assertEqual(len(cleared), 5)
        self.assertEqual(len(sample[0].splitlines()), 6)
        self.assertEqual(sample[1:4], (app.EMPTY, [], None))
        self.assertEqual(cleared[:4], ("", app.EMPTY, [], None))

    def test_empty_overview(self):
        self.assertEqual(app.render_overview([]), app.EMPTY)

    def test_gradio_app_builds(self):
        demo = app.build_app()
        config = demo.get_config_file()
        types = [component["type"] for component in config["components"]]
        self.assertIn("dataframe", types)
        self.assertIn("file", types)
        self.assertEqual(len(config["dependencies"]), 4)
