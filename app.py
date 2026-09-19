"""Course Pulse: a Gradio dashboard built around the workshop's sentiment model."""

import html
import logging
import os

import gradio as gr

from core import (
    HEADERS, MODEL_ID, analyse_comments, inspect_tokens,
    load_sample_feedback, summary_counts, write_report,
)

CSS = """
.gradio-container {max-width:1120px!important; margin:auto!important;}
#masthead {background:#112d36; color:#f7faf8; padding:30px 34px; border-radius:20px; margin:12px 0 14px;}
#masthead .eyebrow {font-size:12px; letter-spacing:2px; color:#a4ddc9; font-weight:700;}
#masthead h1 {font-size:38px; margin:8px 0; line-height:1.15; color:#fff;}
#masthead p {max-width:700px; color:#d6e5e5; font-size:16px; line-height:1.65; margin:0;}
.metrics {display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:16px 0;}
.metric {border:1px solid #dce6e3; border-radius:14px; padding:18px; background:#f7faf8; color:#112d36;}
.metric strong {display:block; font-size:32px; line-height:1.25; margin:5px 0; color:#112d36!important;}
.metric span {font-size:12px; letter-spacing:.7px; text-transform:uppercase; color:#112d36!important;}
.metric small {display:block; color:#49616a; font-size:12px;}
.distribution {display:flex; height:14px; border-radius:8px; overflow:hidden; background:#e0e7e5; margin:12px 0 8px;}
.distribution .pos {background:#14846b;}.distribution .neg {background:#ad5549;}
.chart-caption {font-size:13px; color:var(--body-text-color); margin-bottom:15px;}
.empty-state {border:1px dashed #a8beb7; background:#f7faf8; color:#48616a; padding:22px; border-radius:14px; margin:16px 0;}
.token-wrap {display:flex;flex-wrap:wrap;gap:8px;margin:12px 0;}
.token {display:inline-flex;flex-direction:column;background:#edf5f2;color:#123d33;border:1px solid #bdd7ce;border-radius:8px;padding:7px 11px;}
.token code {font-size:14px;color:#123d33!important;background:transparent!important;}.token small {font-size:11px;color:#546c65;}
@media(max-width:640px){.metrics{grid-template-columns:repeat(2,1fr)}#masthead{padding:22px}#masthead h1{font-size:30px}}
"""

EMPTY = '<div class="empty-state">Your overview will appear here. Start with the sample or paste your own comments.</div>'


def render_overview(rows):
    counts = summary_counts(rows)
    if not counts["total"]:
        return EMPTY
    cards = [("Comments", "total", "Non-empty lines analysed"),
             ("Predicted positive", "positive", "Model classification"),
             ("Predicted negative", "negative", "Model classification"),
             ("Close scores", "review", "Highest score below 80%")]
    result = '<div class="metrics">'
    for title, key, caption in cards:
        result += f'<div class="metric"><span>{title}</span><strong>{counts[key]}</strong><small>{caption}</small></div>'
    result += '</div>'
    positive_width = 100 * counts["positive"] / counts["total"]
    result += (f'<div class="distribution" role="img" aria-label="{counts["positive"]} positive and {counts["negative"]} negative predictions">'
               f'<div class="pos" style="width:{positive_width}%"></div>'
               f'<div class="neg" style="width:{100-positive_width}%"></div></div>'
               '<div class="chart-caption">Green: predicted positive · Terracotta: predicted negative. '
               'These counts describe model predictions, not a measured course satisfaction rate.</div>')
    return result


def run_dashboard(text):
    try:
        rows = analyse_comments(text)
        export = write_report(rows)
        return render_overview(rows), rows, export, "Analysis complete. Read each comment alongside its prediction before drawing conclusions."
    except ValueError as exc:
        gr.Warning(str(exc))
        return EMPTY, [], None, str(exc)
    except Exception:
        logging.exception("Analysis failed")
        message = "The model could not run. If this is the first launch, allow time for its download and try again."
        gr.Warning(message)
        return EMPTY, [], None, message


def run_token_explorer(text):
    try:
        tokens, count = inspect_tokens(text)
        chips = ''.join(f'<span class="token"><code>{html.escape(token)}</code><small>ID {number}</small></span>' for token, number in tokens)
        return f'<div class="token-wrap">{chips}</div>', f"{count} tokens, including special markers. Tokens are not explanations of which words caused the prediction."
    except ValueError as exc:
        return "", str(exc)
    except Exception:
        logging.exception("Token inspection failed")
        return "", "The tokenizer could not load. Please try again after the model download finishes."


def load_sample():
    return load_sample_feedback(), EMPTY, [], None, "Sample loaded. Click Analyse feedback."


def clear_dashboard():
    return "", EMPTY, [], None, "Ready for a new set of comments."


def build_app():
    theme = gr.themes.Soft(primary_hue="teal", secondary_hue="slate", neutral_hue="slate")
    with gr.Blocks(title="Course Pulse | Course Feedback Dashboard", theme=theme, css=CSS, delete_cache=(3600, 3600)) as demo:
        gr.HTML('''<header id="masthead"><div class="eyebrow">COURSE FEEDBACK · EXPLORE, THEN REVIEW</div>
        <h1>Course Pulse</h1><p>Turn a handful of course comments into a clear first overview.
        See the predictions, inspect the words as tokens, and keep people in the loop.</p></header>''')
        with gr.Tab("Feedback dashboard"):
            gr.Markdown("### 1 · Add your feedback\nOne short English comment per line. Up to 30 comments. Use anonymous comments without names or contact details.")
            comments = gr.Textbox(label="Course comments", lines=7, max_lines=12, placeholder="The examples helped me understand the topic.\nThe session moved too quickly.")
            with gr.Row():
                analyse = gr.Button("Analyse feedback", variant="primary")
                sample = gr.Button("Load sample")
                clear = gr.Button("Clear")
            status = gr.Markdown("First analysis may take longer while the model downloads. Sample comments are invented demonstration data.")
            gr.Markdown("### 2 · Read the overview")
            overview = gr.HTML(EMPTY)
            table = gr.Dataframe(headers=HEADERS, datatype=["number", "str", "str", "number", "number", "str"], interactive=False, wrap=True, label="Comment-by-comment predictions")
            report = gr.File(label="Download this analysis as CSV", interactive=False)
            gr.Markdown("**How to read this:** Positive and negative scores add up to about 100%. A high score is not proof. ‘Close scores’ uses an app-defined 80% threshold, not a validated uncertainty measure. This model has no neutral class and may misread mixed opinions, sarcasm, or non-English text.")
            analyse.click(run_dashboard, inputs=comments, outputs=[overview, table, report, status], concurrency_limit=1, concurrency_id="model")
            sample.click(load_sample, outputs=[comments, overview, table, report, status])
            clear.click(clear_dashboard, outputs=[comments, overview, table, report, status])
        with gr.Tab("Inside the model"):
            gr.Markdown("### Watch a sentence become tokens\nThe model receives number IDs, not raw words. Try a sentence, then change a word and inspect it again.")
            sentence = gr.Textbox(label="One short English comment", value="The workshop was not bad at all.", lines=2)
            inspect = gr.Button("Show tokens", variant="primary")
            token_display = gr.HTML()
            token_status = gr.Markdown()
            inspect.click(run_token_explorer, inputs=sentence, outputs=[token_display, token_status], concurrency_limit=1, concurrency_id="model")
            gr.Markdown("**What the markers mean:** `[CLS]` is a special sequence-start marker used for classification; `[SEP]` marks the end or separates sequences; `##` marks a word continuation in this tokenizer.\n\n**The full journey:** text → tokenizer → DistilBERT + classification head → raw scores (logits) → softmax → label scores → dashboard. The pipeline handles these steps. No model training happens when you submit a comment.")
        with gr.Tab("About & limitations"):
            gr.Markdown(f"""### Built from the workshop concepts
Course Pulse brings together sentiment pipelines, tokenization, tabular data, and a Gradio interface.
It adds a batch overview, a transparent review flag, an export, and a token explorer.

### Model and scope
Uses [{MODEL_ID}](https://huggingface.co/{MODEL_ID}), a pretrained English sentiment classifier fine-tuned on SST-2 movie-review data. Course feedback is a different domain; performance here has not been established by a representative evaluation. The pretrained model is credited to its creators and is licensed Apache-2.0.

There are only two model labels: positive and negative. Counts do not measure teaching quality. Even high-confidence predictions need context. Long inputs are rejected rather than silently cut off.

### Data handling
Comments are processed by this running app. They are not used for training or deliberately saved in a database. An analysis creates a temporary CSV for download, subject to host/cache cleanup; do not enter sensitive information. Gradio and the hosting provider operate the service infrastructure.

### Development credit
This workshop project was developed with OpenAI Codex assistance for implementation, explanations, and testing. The model and libraries are third-party work. No claim is made that the model was trained for this project. See the repository README for sources and testing details.
""")
    return demo


if __name__ == "__main__":
    build_app().queue(default_concurrency_limit=1).launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0" if os.environ.get("SPACE_ID") else "127.0.0.1"),
        server_port=int(os.environ.get("PORT", "7860")),
        show_error=False,
    )
