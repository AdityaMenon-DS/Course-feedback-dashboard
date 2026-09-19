# Verification record

Updated 19 September 2026. Tested locally on Windows with Python 3.12, Gradio 5.49.1, Transformers 4.57.6, and PyTorch 2.8.0+cpu. The current assignment requires a Google Drive folder; uploading, public-sharing verification, and form submission remain separate steps.

## Automated checks

All **28 tests passed**: 13 core tests, 8 interface/callback tests, and 7 real-model tests. No tests were skipped in the recorded full run. Run from the repository root with `RUN_MODEL_TESTS=1` and `python -m unittest discover -s tests -v`.

- Reject empty/whitespace input.
- Handle different line endings, ignore blank lines, and preserve duplicate comments.
- Accept 30 comments and reject 31.
- Enforce the character limit.
- Reject token sequences over 512 rather than silently truncating them.
- Associate model scores by label, independently of result order; verify overview counts and review flag.
- Reject a mismatched number of predictions.
- Verify CSV headers, Unicode/quote round trips, formula escaping, and unique export filenames.
- Check a single comment, invalid input types, and a very large paste.
- Read all six sample CSV comments, including quoted commas.
- Validate model label names, finite scores, and score sums.
- Ensure a close-score flag does not introduce a neutral model class.
- Verify callback output order, error messages, stale-result clearing, load/clear actions, and escaped token HTML.
- Verify the Gradio app imports and constructs its tabs, table, file output, and event configuration.
- Compare real pipeline results with a direct forward pass and `torch.softmax`.
- Run actual single, multiple, positive, negative, and mixed-comment inference; check real callback CSV generation.

The isolated package environment passed `pip check` with no broken requirements.

## Real model checks

Model revision observed during testing: `714eb0fa89d2f80546fda750413ed43d93601a13`.

| Input | Prediction | Positive score | Negative score |
|---|---|---:|---:|
| The explanations were excellent and very helpful. | Positive | 99.98% | 0.02% |
| The lesson was terrible and confusing. | Negative | 0.06% | 99.94% |
| The course was useful, but the explanations were sometimes confusing. | Negative | 0.34% | 99.66% |

The six-comment sample produced 3 positive and 3 negative predictions. This is a functional smoke test, not a measured accuracy score.

The mixed-comment example was confidently negative, so it did not trigger the close-score flag. The close-score branch is separately tested using explicitly synthetic 51% / 49% scores. Mixed meaning and low model confidence are not equivalent.

Additional checks passed for real tokenizer IDs, special tokens, actual overlong-token rejection, stale-output clearing after invalid input, HTML escaping in token output, and construction of the Gradio event configuration.

## Observed model error — retained for discussion

The comment **“The worked examples made the topic much easier to understand.”** reads as positive feedback, but the model predicted **Negative (91.22%)** in the browser test. It remains in the demonstration sample to show that confidence does not establish correctness, and that movie-review training does not guarantee performance on course feedback.

## Browser verification

The local Gradio page loaded; Load sample populated six comments; Analyse feedback produced the overview, a six-row table, and a CSV download link. The token viewer returned 10 tokens for “The workshop was not bad at all.” Visual inspection identified a dark-mode contrast issue in token chips, and the CSS was corrected.

The final repository was run separately from the earlier prototype, with the sample loaded from `sample_data/sample_feedback.csv`. Markdown parsing verified the README/guide code fences and local links. A source scan found no matching Hugging Face/GitHub credential patterns, private-key markers, or user-specific Windows paths. This is a focused check, not a guarantee that every possible secret format is detectable.

Final browser screenshots confirmed readable summary labels and token chips in dark mode after the CSS fixes. The live CSV download endpoint returned the expected headers and six data rows. Google Drive showed a sign-in page in the available browser. No Drive upload or form submission has been completed.

## Warnings observed

The Windows test run emitted Gradio/asyncio resource warnings while constructing a temporary interface; all assertions completed successfully. The overlong-input test intentionally caused a tokenizer length warning before the application rejected that input. No model inference was attempted on the overlong sequence. These warnings are recorded rather than suppressed.

## Limits of verification

These checks do not establish model accuracy, fairness, or confidence calibration on a representative course-feedback dataset. This project does not train the model. The final Drive folder must still be uploaded and its public access checked before form submission. No grading or plagiarism-detector outcome is guaranteed.

## Drive bundle verification

All 28 tests passed again from the actual submission folder with HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1, and a separate initially empty Hugging Face cache directory. The included model files were loaded locally. The bundled app launched on a separate local port and returned HTTP 200. Its live Gradio API produced six sample predictions, a downloadable CSV with a header and six rows, and token output. This verifies offline model inference after dependencies are installed; installation of Python libraries still requires internet.
