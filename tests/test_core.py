"""Run: python -m unittest discover -s tests -v (no model download required)."""

import csv
from pathlib import Path
import unittest

from core import HEADERS, check_token_lengths, load_sample_feedback, make_rows, parse_comments, summary_counts, write_report


class InputTests(unittest.TestCase):
    def test_blank_input_is_rejected(self):
        for value in [None, "", " \n\t", 123, ["hello"]]:
            with self.assertRaises(ValueError):
                parse_comments(value)

    def test_one_comment(self):
        self.assertEqual(parse_comments(" A useful lesson. "), ["A useful lesson."])

    def test_oversized_paste(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            parse_comments("x" * 61000)

    def test_sample_csv(self):
        comments = parse_comments(load_sample_feedback())
        self.assertEqual(len(comments), 6)
        self.assertIn(", although", comments[-1])

    def test_line_breaks_and_repeated_comments_are_preserved(self):
        self.assertEqual(parse_comments(" Good \r\n\r\nBad\nGood "), ["Good", "Bad", "Good"])

    def test_comment_limit(self):
        self.assertEqual(len(parse_comments("\n".join(["OK"] * 30))), 30)
        with self.assertRaises(ValueError):
            parse_comments("\n".join(["OK"] * 31))

    def test_character_limit(self):
        parse_comments("a" * 2000)
        with self.assertRaises(ValueError):
            parse_comments("a" * 2001)

    def test_overlong_tokens_rejected_not_silently_truncated(self):
        class Tokenizer:
            model_max_length = 512

            def __call__(self, comments, **kwargs):
                return {"input_ids": [list(range(int(comment))) for comment in comments]}

        check_token_lengths(["512"], Tokenizer())
        with self.assertRaisesRegex(ValueError, "Comment 2 has 513 tokens"):
            check_token_lengths(["10", "513"], Tokenizer())


class OutputTests(unittest.TestCase):
    def test_scores_mapped_by_label_not_list_position(self):
        predictions = [[{"label": "NEGATIVE", "score": 0.2}, {"label": "POSITIVE", "score": 0.8}],
                       [{"label": "POSITIVE", "score": 0.49}, {"label": "NEGATIVE", "score": 0.51}]]
        rows = make_rows(["A", "B"], predictions)
        self.assertEqual(rows[0][2:5], ["Positive", 80.0, 20.0])
        self.assertEqual(rows[1][2], "Negative")
        self.assertEqual(summary_counts(rows), {"total": 2, "positive": 1, "negative": 1, "review": 1})

    def test_prediction_count_mismatch(self):
        with self.assertRaises(ValueError):
            make_rows(["A", "B"], [[]])

    def test_invalid_model_labels_and_scores(self):
        for prediction in [
            [{"label": "NEUTRAL", "score": 1}],
            [{"label": "POSITIVE", "score": float("nan")}, {"label": "NEGATIVE", "score": 0.5}],
            [{"label": "POSITIVE", "score": 0.6}, {"label": "NEGATIVE", "score": 0.6}],
        ]:
            with self.assertRaises(ValueError):
                make_rows(["text"], [prediction])

    def test_close_scores_do_not_create_a_neutral_class(self):
        rows = make_rows(["Mixed"], [[{"label": "POSITIVE", "score": 0.51}, {"label": "NEGATIVE", "score": 0.49}]])
        self.assertEqual(rows[0][2], "Positive")
        self.assertTrue(rows[0][5].startswith("Close scores"))

    def test_csv_roundtrip_and_formula_escape(self):
        rows = [[1, '=HYPERLINK("example")', "Positive", 90.0, 10.0, "Check"],
                [2, 'Good, with "examples" — helpful', "Positive", 95.0, 5.0, "Check"]]
        first, second = write_report(rows), write_report(rows)
        try:
            self.assertNotEqual(first, second)
            with open(first, encoding="utf-8-sig", newline="") as stream:
                data = list(csv.reader(stream))
            self.assertEqual(data[0], HEADERS)
            self.assertTrue(data[1][1].startswith("'="))
            self.assertEqual(data[2][1], rows[1][1])
        finally:
            Path(first).unlink()
            Path(second).unlink()


if __name__ == "__main__":
    unittest.main()
