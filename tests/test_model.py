"""Opt in with RUN_MODEL_TESTS=1. These tests load the real public model."""

import csv
import os
from pathlib import Path
import unittest

from core import MODEL_ID, analyse_comments, get_classifier, inspect_tokens, load_sample_feedback


@unittest.skipUnless(os.environ.get("RUN_MODEL_TESTS") == "1", "Set RUN_MODEL_TESTS=1 to test the real model")
class RealModelTests(unittest.TestCase):
    def test_clearly_positive_and_negative(self):
        rows = analyse_comments("The explanations were excellent and very helpful.\nThe lesson was terrible and confusing.")
        self.assertEqual([row[2] for row in rows], ["Positive", "Negative"])

    def test_single_and_mixed_feedback(self):
        one = analyse_comments("The course was useful, but the explanations were sometimes confusing.")
        self.assertEqual(len(one), 1)
        self.assertIn(one[0][2], ("Positive", "Negative"))
        self.assertAlmostEqual(one[0][3] + one[0][4], 100.0, places=1)

    def test_multiple_sample_comments(self):
        self.assertEqual(len(analyse_comments(load_sample_feedback())), 6)

    def test_manual_logits_softmax_match_pipeline(self):
        import torch
        classifier = get_classifier()
        self.assertEqual(classifier.model.config.model_type, "distilbert")
        self.assertEqual(set(classifier.model.config.id2label.values()), {"POSITIVE", "NEGATIVE"})
        text = "The lesson was excellent."
        inputs = classifier.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = classifier.model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0].tolist()
        expected = {classifier.model.config.id2label[i]: score for i, score in enumerate(probabilities)}
        actual = {item["label"]: item["score"] for item in classifier(text)[0]}
        for label in expected:
            self.assertAlmostEqual(actual[label], expected[label], places=5)

    def test_token_viewer(self):
        tokens, count = inspect_tokens("The workshop was not bad at all.")
        self.assertEqual(count, len(tokens))
        self.assertEqual(tokens[0], ("[CLS]", 101))
        self.assertEqual(tokens[-1], ("[SEP]", 102))

    def test_model_token_limit(self):
        with self.assertRaisesRegex(ValueError, "tokens"):
            analyse_comments("a " * 600)

    def test_real_callback_and_csv(self):
        from app import run_dashboard
        overview, rows, filename, status = run_dashboard("I loved the clear explanations.")
        self.assertEqual(len(rows), 1)
        self.assertIn("complete", status)
        self.assertIn("1 positive", overview)
        try:
            with open(filename, encoding="utf-8-sig", newline="") as stream:
                exported = list(csv.reader(stream))
            self.assertEqual(len(exported), 2)
            self.assertEqual(exported[1][1], rows[0][1])
        finally:
            if filename:
                Path(filename).unlink(missing_ok=True)
