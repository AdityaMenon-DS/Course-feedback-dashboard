# Start here: Google Drive assignment submission

The instructor's updated instructions require a Google Drive folder containing a working Gradio application. A live Space is no longer required.

**Deadline: Thursday, 24 September 2026.**

## What to upload

Extract `course-feedback-dashboard-drive.zip`. Upload the complete extracted **course-feedback-dashboard** folder to Drive. Do not submit only a ZIP, only `app.py`, or the earlier source-only ZIP.

Required runtime files in the Drive bundle:

```text
course-feedback-dashboard/
├── app.py
├── core.py
├── requirements.txt
├── sample_data/
│   └── sample_feedback.csv
└── model/
    ├── config.json
    ├── model.safetensors
    ├── tokenizer_config.json
    ├── vocab.txt
    ├── README.md
    ├── LICENSE-APACHE-2.0.txt
    └── MODEL_INFO.md
```

Keep the accompanying project README, license, test files, testing record, and learning guide too. They explain and document the project. No `.joblib` or `.pkl` file is needed: this application uses Hugging Face's `.safetensors` model format.

## How the evaluator can run it

Install Python **3.12**, open a terminal inside the downloaded project folder, and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:7860**. Internet is needed to install libraries, but the bundled model supports offline inference afterwards. On Linux, use `python3.12 -m venv .venv` and `.venv/bin/python` for the subsequent commands.

Try **Load sample → Analyse feedback**, **Inside the model → Show tokens**, and CSV download. The app loads files relative to its own folder; it does not depend on the author's machine paths.

## Upload and share

1. In Google Drive, select **New → Folder upload**.
2. Choose the extracted `course-feedback-dashboard` folder.
3. Wait for the entire upload to finish, including `model/model.safetensors` (about 268 MB).
4. Right-click the uploaded folder and choose **Share**.
5. Under **General access**, select **Anyone with the link** and the **Viewer** role.
6. Click **Done**, then copy the folder link.
7. Open the link in a signed-out/private browser window. Confirm that the folder and its files can be viewed and downloaded. Make sure you did not accidentally copy a local path or an individual file link.
8. Submit the folder link using https://forms.gle/QPxDBQjKGJe5EoQb7 and save the confirmation.

If the form still calls its URL field a Gradio/Space link, the instructor's updated message says to enter the **Drive folder link** in that same form.

## Honest authorship

The application workflow and integration were developed for this assignment with OpenAI Codex assistance. DistilBERT and its pretrained weights are credited third-party work. Keep the model attribution, application license, and AI-assistance disclosure. No plagiarism-detector outcome can be guaranteed.

Before submission, read `LEARNING_GUIDE.md`, run examples you wrote yourself, and explain why a mixed comment might receive a confident binary prediction. Any personal-contribution statement should describe work you actually performed. If your instructor restricts AI assistance, follow that rule rather than concealing the assistance.
