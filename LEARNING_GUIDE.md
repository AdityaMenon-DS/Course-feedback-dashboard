# Understand and demonstrate Course Pulse

## 1. The problem

A teacher has several short course comments. Reading all of them is still necessary, but a first overview can help organise that work. Course Pulse predicts positive/negative sentiment, shows every original comment beside its scores, and exports the results. It does not grade a teacher or measure course satisfaction.

## 2. Connect the files to the lectures

| File or feature | What it does | Workshop connection |
|---|---|---|
| `core.py`, `get_classifier()` | Loads a pretrained model through a pipeline | Lecture 1: inference |
| `parse_comments()` | Turns pasted lines into a list | Lists and data preparation |
| `make_rows()` | Extracts each label score and creates table rows | Feedback table exercise |
| `inspect_tokens()` | Shows token strings and numerical IDs | Lectures 1–2: tokenization |
| `app.py`, `build_app()` | Creates the screen and connects buttons to functions | Lecture 2: Gradio |
| `requirements.txt` | Names exact software versions | Reproducible setup |
| `README.md` | Describes the project and configures its Space | Assignment deployment |

## 3. Trace one request

Suppose the visitor enters these two lines:

```text
The examples were clear and useful.
The explanations were rushed and confusing.
```

1. The Analyse button passes the textbox contents to `run_dashboard()`.
2. `parse_comments()` splits at line breaks and removes blank lines.
3. `get_classifier()` returns the loaded pipeline. The cache avoids downloading/reloading the model for every click.
4. `check_token_lengths()` rejects a comment that is too long for the model. Nothing is silently cut off.
5. The pipeline tokenizes the list and runs the model in batches of up to eight.
6. `top_k=None` asks for all class scores, so both positive and negative can be displayed.
7. `make_rows()` uses the labels, not the order of returned scores, to build the table.
8. `summary_counts()` counts predicted classes. A separate rule flags comments whose highest score is below 0.80.
9. `write_report()` writes a separate CSV for this request.
10. Gradio updates the overview, table, download, and status message.

## 4. Important Python to recognise

```python
comments = [line.strip() for line in text.splitlines() if line.strip()]
```

Read it as: “For each line, remove outer spaces; keep it if it is not blank; collect the results into a list.”

```python
scores = {item["label"].upper(): float(item["score"]) for item in prediction}
```

This creates a dictionary so the positive score can be looked up by `scores["POSITIVE"]`. It is safer than assuming the first returned score always belongs to positive sentiment.

```python
@lru_cache(maxsize=1)
def get_classifier():
    ...
```

The decorator remembers the loaded model. Think of opening a textbook once and keeping it open instead of getting a new copy for every question.

```python
analyse.click(run_dashboard, inputs=comments, outputs=[overview, table, report, status])
```

This connects a button to a Python function. The input textbox supplies the argument. The returned values fill the listed outputs in order.

## 5. What is original, and what is reused?

The app workflow, course-oriented sample comments, validation, dashboard, token viewer, and their integration were developed for this project with Codex assistance. The pretrained model, Gradio, PyTorch, and Transformers are reused tools. Standard API calls will naturally resemble documentation; do not claim those APIs or the model as original inventions.

Keep the references and AI-assistance disclosure. Do not claim you trained the model or independently wrote code you have not understood. No plagiarism or AI detector score is promised. If the instructor has a restriction on AI assistance, that rule determines what you can submit.

## 6. Small changes to make after you understand the app

- Replace the fictional sample with your own anonymous, invented course comments.
- Adjust the title or description so it fits the situation you want to demonstrate.
- Explain why the 80% threshold was chosen as a visible review rule, and why it is not a guarantee of correctness.
- Record one example where you disagree with the model. Explain the missing context instead of hiding the mistake.

Do not change names just to disguise where the work came from. Make changes because you can explain their purpose.

## 7. A two-minute demonstration

1. Explain the problem in one sentence.
2. Load the sample and analyse it.
3. Point to one comment and its two scores.
4. Explain that counts refer to predictions, not actual student satisfaction.
5. Open Inside the model, inspect a sentence, and explain one token ID.
6. Download the CSV.
7. State one limitation and credit the pretrained model.

## 8. Ten likely viva questions

**Did you train a model?** No. The application performs inference with a public pretrained classifier.

**Why can it get feedback wrong?** It learned from movie-review sentiment data, has only two labels, and can miss context, sarcasm, and mixed opinions.

**What does a token mean?** A piece of text mapped to a number; it may be a whole word, part of a word, or a special marker.

**What is the review flag?** An application rule: the largest model score is below 80%. High scores can still be wrong.

**What makes it more than the sample pipeline?** Multiple comments, explicit limits, overview counts, both class scores, downloadable results, and token inspection in one Gradio interface.

**What did AI help with?** Implementation, explanations, and testing. Describe your own actual review, modifications, and testing accurately.

**What are logits and softmax?** Logits are raw category scores. Softmax converts them into positive/negative scores that add up to one. The pipeline performs this step.

**Why separate app.py and core.py?** One file handles the screen; the other handles analysis. That makes the code easier to read and test.

**What does the dataset do here?** The sample CSV supplies fictional comments for demonstration. It is not training data used to change the model.

**How did you test it?** Input validation and callback tests check the software, while real-model tests check predictions, token IDs, CSV output, and agreement between manual softmax and the pipeline. These tests do not establish real-world accuracy.

## 9. Current submission requirement

The instructor now requires a **Google Drive folder link** containing the runnable application and supporting files. A live Hugging Face Space is no longer required. Use the folder in the Drive submission bundle and follow `SUBMISSION.md`.

Form: https://forms.gle/QPxDBQjKGJe5EoQb7

Deadline: Thursday, 24 September 2026. Share the folder as **Anyone with the link → Viewer**, and test its accessibility before submitting. If the form's label still mentions a Gradio/Space URL, follow the instructor's newer instruction and put the Drive folder link in that link field.

## 10. Git and GitHub, explained simply

Git is a local record of your project's saved versions. GitHub is an online place to share that record. Hugging Face Spaces is where the app runs.

| Command | Meaning |
|---|---|
| `git status` | Show which files changed and what is ready to save. |
| `git add` | Select changes for the next saved version. |
| `git commit` | Create a local saved version with an explanatory message. |
| `git push` | Send your local commits to the online repository. |
| `git pull` | Bring online commits into your local copy and integrate them. |

### First upload

1. Sign in to GitHub, click **+ → New repository**, and name it `course-feedback-dashboard`.
2. Choose visibility. Public makes it easy for an evaluator to inspect the code; use private if your course requires it.
3. When pushing this prepared repository, leave GitHub's README, license, and gitignore initialisation options unchecked.
4. Click **Create repository** and copy its HTTPS URL.
5. In the project's terminal, run `git status`, `git log --oneline -3`, and `git remote -v` to see what is already set up.

If Git is not initialised (for example, after extracting the ZIP):

```bash
git init
git add .
git commit -m "Initial version of Course Feedback Dashboard"
git branch -M main
```

If a local commit already exists, skip that block. Do not invent earlier commits or split existing work into a fake history. Then:

```bash
git remote add origin <MY_REPOSITORY_URL>
git push -u origin main
```

Replace `<MY_REPOSITORY_URL>` before running it. If an origin already exists, check that it is the intended repository instead of blindly overwriting it. Complete authentication through Git's browser flow, an existing SSH setup, or GitHub Desktop. Do not enter your GitHub account password as a Git HTTPS password.

If Git says it needs an author identity, set your own name and GitHub no-reply email in this repository:

```bash
git config user.name "Your Name"
git config user.email "Your GitHub no-reply email"
```

### Upload with browser buttons instead

In an empty GitHub repository choose **uploading an existing file**; in an existing repository use **Add file → Upload files**. Upload the project contents with the `tests/` and `sample_data/` paths intact, then **Commit changes**. Do not upload `.git`, `.venv`, model downloads, caches, or your ZIP. The `.gitignore` is a hidden file on some systems, so confirm it appears in the uploaded file list.

### Future edits

```bash
git status
git add app.py core.py README.md
git commit -m "Describe the actual change"
git push
```

Run `git pull` before editing if the online repository has changes made elsewhere. Read and resolve conflicts rather than using a destructive reset.

## 11. The submission flow

```text
Tested project + bundled pretrained model
        ↓ upload the extracted folder
Google Drive folder
        ↓ Anyone with the link → Viewer
Verify from a signed-out browser
        ↓
Submit the Drive folder URL in the workshop form
```

The evaluator downloads the folder, installs `requirements.txt`, and runs `app.py`. Keep `model/` and `sample_data/` beside the source files. GitHub and live hosting are optional portfolio steps.

## 12. One-minute explanation

“I built Course Pulse, a course-feedback dashboard using Python and Gradio. Users paste one comment per line. The app validates the input and uses a pretrained DistilBERT sentiment model through Hugging Face Transformers. A tokenizer converts text into IDs; the model produces logits; softmax turns them into positive and negative scores. The dashboard shows each prediction, counts the labels, flags close scores, and exports a CSV. A second tab displays the actual tokens and IDs. I separated the interface from the analysis code and tested input validation, callbacks, the tokenizer, and real model predictions. I did not train DistilBERT. It has no neutral class and sometimes makes confident mistakes, so people should read the original comments. Codex assisted with development, documentation, and tests.”

## 13. Submission checklist

- Add your name where appropriate and describe your actual contribution honestly.
- Understand the model limitations, sources, and AI-assistance disclosure.
- Extract the provided Drive ZIP and keep its folder structure.
- Run the app using Python 3.12 and the supplied requirements.
- Try your own positive, negative, and mixed comments; inspect tokens and download a CSV.
- Upload the entire extracted project folder, including `model/` and `sample_data/`.
- Wait for all uploads to finish.
- Set **Anyone with the link → Viewer** on the folder.
- Open the folder while signed out and verify the files are accessible/downloadable.
- Submit the Drive folder link in the assignment form.
- Save the submission confirmation before Thursday, 24 September 2026.
