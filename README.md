---
title: Course Pulse
emoji: 📚
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.49.1
python_version: '3.12'
app_file: app.py
short_description: A course feedback dashboard with a token explorer
license: mit
models:
  - distilbert/distilbert-base-uncased-finetuned-sst-2-english
tags:
  - sentiment-analysis
  - education
  - gradio
---

# Course Feedback Dashboard · Course Pulse

A Gradio application that turns short English course comments into an inspectable sentiment overview. Paste one comment per line, see both model scores, download the results, and explore the tokenizer.

**Status:** locally tested; see [TESTING.md](TESTING.md) for evidence. The updated assignment requires a **Google Drive folder link**, not a live Space. See [SUBMISSION.md](SUBMISSION.md). Upload and form submission must still be completed.

## The problem

A teacher may receive many short comments after a course. Course Pulse provides a first overview while keeping the original comments visible. It helps organise review; it does not replace reading feedback or measure teaching quality.

## Features

- Analyse one or up to 30 comments at a time.
- Show positive/negative predictions and both softmax scores.
- Count total, predicted-positive, predicted-negative, and close-score comments.
- Flag predictions whose highest score is below 80% for closer human review.
- Display a results table and download a CSV report.
- Inspect a sentence's token pieces and numerical IDs.
- Load six fictional sample comments from a CSV file.
- Reject blank, invalid, excessive, or overlong input without silently cutting text.
- Explain model limitations and credit the model and libraries.

## Architecture and information flow

```text
Textbox or sample CSV
       |
       v
app.py: Gradio button calls run_dashboard()
       |
       v
core.py: validate and split comments
       |
       v
Tokenizer -> DistilBERT + classification head -> logits -> softmax
       |
       v
Labels + both scores -> review flags + counts + CSV
       |
       v
app.py: overview cards, table, and download
```

`app.py` owns the interface. `core.py` owns data preparation, model loading, predictions, token inspection, and report generation. Separating them allows the analysis to be tested without clicking the interface.

### What the model does

1. **Tokenizer:** divides text into tokens and converts them into number IDs. A token may be a word, a word piece, punctuation, or a special marker.
2. **Model:** processes those IDs and creates numerical representations of the sentence.
3. **Classification head:** produces two raw scores called **logits**, one per label.
4. **Softmax:** converts the logits into positive/negative scores between 0 and 1 that add up to 1. The pipeline explicitly requests this operation.
5. **Label:** the larger score determines the prediction. The app reads scores by their label names, not their returned position.

For example, hypothetical scores of 0.51 positive and 0.49 negative produce a positive prediction and a close-score flag. They do **not** produce a neutral class. Softmax scores are not calibrated guarantees of correctness.

The project performs **inference only**. It does not train or fine-tune DistilBERT. Tests compare pipeline scores with a direct model-forward-pass plus `torch.softmax` calculation.

## Technologies

| Technology | Role |
|---|---|
| Python 3.12 | Application language |
| Transformers 4.57.6 | Pipeline and tokenizer/model loading |
| PyTorch 2.8.0 CPU | Model calculations |
| Gradio 5.49.1 | Browser interface and event handling |
| Python `csv` and `unittest` | Sample/report files and tests |

`requirements.txt` lists only application dependencies. Libraries needed internally by Gradio or Transformers are installed automatically. These versions were tested together in an isolated environment; do not run a blanket upgrade in an existing Colab environment.

## Install and run locally

Use Python **3.12** and an ordinary CPU. Internet is needed to install the Python libraries. The Drive submission includes the pretrained model in `model/`, so model inference can run offline after installation. The smaller source-only version downloads the same model on first use. The CPU requirements target Windows/Linux.

### Windows PowerShell

Open a terminal inside the repository folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

No environment activation is required because the commands explicitly use its Python executable. If `py` is not available, install Python 3.12 and reopen the terminal, or replace `py -3.12` with the path to your Python 3.12 executable.

### Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open **http://127.0.0.1:7860**. If `model/` is present beside `app.py`, the app loads those bundled weights and tokenizer files. Otherwise, the first analysis downloads approximately 268 MB of model weights plus tokenizer files. Python packages are separate downloads. No model API key is required. Stop the server with Ctrl+C. If port 7860 is occupied, set `PORT` to another port before running the app.

## Example usage

1. Click **Load sample**, or paste:

   ```text
   The explanations were excellent and very helpful.
   The lesson was terrible and confusing.
   The course was useful, but some explanations were confusing.
   ```

2. Click **Analyse feedback**.
3. Read the original comments and scores together; do not interpret counts as a satisfaction survey.
4. Download the CSV.
5. Open **Inside the model**, enter one sentence, and click **Show tokens**.

Edit `sample_data/sample_feedback.csv` to customise the demonstration. Preserve the `feedback` header and quote CSV fields containing commas. The sample is fictional, not a real student dataset.

## Repository structure

```text
course-feedback-dashboard/
├── app.py
├── core.py
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
├── LEARNING_GUIDE.md
├── TESTING.md
├── SUBMISSION.md
├── tests/
│   ├── test_core.py
│   ├── test_app.py
│   └── test_model.py
└── sample_data/
    └── sample_feedback.csv
```

The Drive bundle additionally includes `model/` with weights, tokenizer/configuration files, the original model card, and its Apache-2.0 license. Model binaries are excluded from the lightweight Git repository.

The learning guide contains code explanations, Git instructions, viva preparation, and a submission checklist. The testing record distinguishes actual checks from unverified claims.

## Run the tests

Fast tests use controlled inputs and mocked predictions, without downloading a model:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

To include real-model tests in PowerShell:

```powershell
$env:RUN_MODEL_TESTS = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On Linux, use `RUN_MODEL_TESTS=1 .venv/bin/python -m unittest discover -s tests -v`.

Real-model tests cover positive, negative, mixed, single and multiple comments, model label mapping, tokenizer output, logits/softmax equivalence, callback outputs, and CSV generation. Functional tests are not an accuracy benchmark.

## Model information and attribution

- **Model:** [distilbert/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).
- **Model revision:** `714eb0fa89d2f80546fda750413ed43d93601a13`, pinned in `core.py`.
- **Creators:** Hugging Face / DistilBERT model authors; this application does not claim authorship of their model.
- **Task:** binary English sentiment classification; fine-tuned on SST-2 movie-review data.
- **Model license:** Apache-2.0, as stated in the model card. The application code uses the [MIT license](LICENSE); third-party licenses remain separate.

## Limitations and an observed mistake

- Only **POSITIVE** and **NEGATIVE** labels exist. Neutrality is not detected.
- Movie-review training may not transfer reliably to course feedback.
- Sarcasm, mixed opinions, factual statements, and unfamiliar wording can be misclassified.
- Non-English input is outside the intended scope; the app does not automatically detect language.
- Confidence can be high when a prediction is wrong. The 80% review threshold is an interface rule, not a calibrated uncertainty estimate.
- Limits: 30 non-empty lines, 2,000 characters per comment, and 512 tokens including special markers.
- The token viewer shows preprocessing, not which words caused a decision.

**Observed example:** “The worked examples made the topic much easier to understand.” reads as positive feedback, but the tested model predicted **negative with 91.22% confidence**. This example remains in the sample so the limitation is visible. See [TESTING.md](TESTING.md).

## Responsible use and data handling

Use anonymous demonstration comments. Do not use the output alone for grading, teacher evaluation, or consequential decisions about people. A human should read the original text and consider context.

The app does not train on comments or deliberately maintain a feedback database. Each successful run creates a unique temporary CSV. Gradio cache cleanup is enabled, but source/export files can remain temporarily on the host; this is not a zero-retention service. Avoid personal or sensitive information. Formula-like values are escaped when exported to reduce spreadsheet-formula execution risk.

## Submit through Google Drive — current assignment

Follow [SUBMISSION.md](SUBMISSION.md). Upload the extracted `course-feedback-dashboard` folder, including `model/` and `sample_data/`. Set **General access → Anyone with the link → Viewer**, verify the folder from a signed-out browser, then submit its folder link through [the assignment form](https://forms.gle/QPxDBQjKGJe5EoQb7). The deadline supplied by the instructor is **Thursday, 24 September 2026**. A live Space is no longer required.

## Publish on GitHub — optional

Create an empty repository named **course-feedback-dashboard** in your own GitHub account. Do not add another README, license, or `.gitignore` during creation when pushing this existing project.

Inspect first:

```bash
git status
git remote -v
git log --oneline -3
```

For a freshly extracted ZIP without Git history:

```bash
git init
git add .
git commit -m "Initial version of Course Feedback Dashboard"
git branch -M main
```

For an existing local repository with an initial commit, skip those initialisation steps. Then replace the placeholder with the actual empty GitHub repository URL:

```bash
git remote add origin <MY_REPOSITORY_URL>
git push -u origin main
```

If `origin` already exists, inspect its URL instead of adding it again. Use Git's normal browser authentication, SSH, or GitHub Desktop. Never place credentials in source files or paste them into this project's chat. Git needs your own author name/email configured before a commit; a GitHub-provided no-reply email can protect your private address.

See [LEARNING_GUIDE.md](LEARNING_GUIDE.md) for the browser upload alternative and a simple explanation of each Git command.

## Hosting is optional

The instructor's updated requirement supersedes the earlier live-Space submission instructions. No Hugging Face deployment or automatic syncing is needed for certificate submission. The README retains Gradio SDK metadata for future hosting if available, but the graded deliverable is the publicly viewable Drive folder.

## Sources and AI assistance

The project follows concepts taught in the Hugging Face workshop on 16–17 September 2026. Standard API usage is informed by [Transformers pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines), [Gradio documentation](https://www.gradio.app/docs), and the [Gradio Spaces guide](https://huggingface.co/docs/hub/spaces-sdks-gradio).

OpenAI Codex assisted with application design, implementation, documentation, explanations, and testing. The workflow and integration were developed for this project; no other student's repository was used as a template. The pretrained model and libraries are credited third-party components. The submitting learner should describe their actual review, changes, and understanding accurately and follow the instructor's AI-use rules. No originality-detector score or grade is promised.

## Author

- **Name:** Add your name before submission.
- **Roll number:** Add if required by your instructor; consider keeping it in the submission form instead of a public repository.
- **Course / institution:** Add if required.
- **Personal contribution:** Describe the parts you reviewed, changed, tested, and can explain. Do not claim to have trained the pretrained model.
