"""Small, testable pieces of Course Pulse. No UI code lives here."""

import csv
import math
import os
import tempfile
from functools import lru_cache
from pathlib import Path

MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
MODEL_REVISION = "714eb0fa89d2f80546fda750413ed43d93601a13"
MAX_COMMENTS = 30
MAX_CHARACTERS = 2000
REVIEW_THRESHOLD = 0.80
HEADERS = ["#", "Feedback", "Prediction", "Positive score (%)", "Negative score (%)", "Review note"]


def parse_comments(text):
    """Keep one non-empty line per comment. Never silently discard a long input."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste at least one comment, with one comment per line.")
    if len(text) > MAX_COMMENTS * (MAX_CHARACTERS + 2):
        raise ValueError("This paste is too large. Use up to 30 short comments.")
    comments = [line.strip() for line in text.splitlines() if line.strip()]
    if len(comments) > MAX_COMMENTS:
        raise ValueError("Please use at most 30 comments per run.")
    for number, comment in enumerate(comments, start=1):
        if len(comment) > MAX_CHARACTERS:
            raise ValueError(f"Comment {number} is too long. Use at most {MAX_CHARACTERS:,} characters per comment.")
    return comments


def load_sample_feedback():
    """Resolve the sample relative to this file, not the terminal's directory."""
    sample_path = Path(__file__).parent / "sample_data" / "sample_feedback.csv"
    with sample_path.open(encoding="utf-8", newline="") as stream:
        return "\n".join(row["feedback"] for row in csv.DictReader(stream))


@lru_cache(maxsize=1)
def get_classifier():
    # Import lazily: the page can open before the first model download completes.
    from transformers import pipeline

    # The Drive submission includes this folder; the source-only version downloads it.
    bundled_model = Path(__file__).parent / "model"
    model_source = str(bundled_model) if bundled_model.is_dir() else MODEL_ID
    return pipeline(
        "sentiment-analysis", model=model_source, revision=MODEL_REVISION,
        device=-1, top_k=None, function_to_apply="softmax",
    )


def check_token_lengths(comments, tokenizer):
    # The model accepts at most 512 tokens, including its special markers.
    limit = min(int(tokenizer.model_max_length), 512)
    encoded = tokenizer(comments, truncation=False, add_special_tokens=True)
    for number, ids in enumerate(encoded["input_ids"], start=1):
        if len(ids) > limit:
            raise ValueError(f"Comment {number} has {len(ids)} tokens; the limit is {limit}. Shorten it and try again.")


def make_rows(comments, predictions):
    if len(comments) != len(predictions):
        raise ValueError("The model returned an unexpected number of predictions.")
    rows = []
    for number, (comment, prediction) in enumerate(zip(comments, predictions), start=1):
        scores = {item["label"].upper(): float(item["score"]) for item in prediction}
        if set(scores) != {"POSITIVE", "NEGATIVE"}:
            raise ValueError("Expected positive and negative scores from the model.")
        positive, negative = scores["POSITIVE"], scores["NEGATIVE"]
        if not all(math.isfinite(score) and 0 <= score <= 1 for score in (positive, negative)):
            raise ValueError("The model returned an invalid score.")
        if not math.isclose(positive + negative, 1.0, abs_tol=0.001):
            raise ValueError("The two model scores should add up to one.")
        label = "Positive" if positive >= negative else "Negative"
        note = "Close scores — review manually" if max(positive, negative) < REVIEW_THRESHOLD else "Check against the original text"
        rows.append([number, comment, label, round(positive * 100, 2), round(negative * 100, 2), note])
    return rows


def analyse_comments(text):
    comments = parse_comments(text)
    classifier = get_classifier()
    check_token_lengths(comments, classifier.tokenizer)
    predictions = classifier(comments, batch_size=8, truncation=False)
    return make_rows(comments, predictions)


def summary_counts(rows):
    return {
        "total": len(rows),
        "positive": sum(row[2] == "Positive" for row in rows),
        "negative": sum(row[2] == "Negative" for row in rows),
        "review": sum(row[5].startswith("Close scores") for row in rows),
    }


def safe_csv_cell(value):
    # Spreadsheet apps may execute cells starting with these characters as formulas.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_report(rows):
    # Unique files keep different visitors' exports separate.
    fd, filename = tempfile.mkstemp(prefix="course-pulse-", suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADERS)
        writer.writerows([[safe_csv_cell(cell) for cell in row] for row in rows])
    return filename


def inspect_tokens(text):
    comments = parse_comments(text)
    if len(comments) != 1:
        raise ValueError("Use one comment in the token explorer.")
    tokenizer = get_classifier().tokenizer
    check_token_lengths(comments, tokenizer)
    encoded = tokenizer(comments[0], add_special_tokens=True)
    ids = encoded["input_ids"]
    tokens = tokenizer.convert_ids_to_tokens(ids)
    return list(zip(tokens, ids)), len(ids)
