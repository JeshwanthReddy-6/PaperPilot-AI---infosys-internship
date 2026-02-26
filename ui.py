import gradio as gr
from main import run_pipeline
from llm_drafting import call_funstion
from tf_idf import compute_similarity
from pdf_convert import text_to_pdf
from refine import refine_synthesized_paper
import os

# -------------------------
# Backend wrappers
# -------------------------

def run_pipeline_ui(topic, limit):
    try:
        fetched, downloaded, pdfs = run_pipeline(topic, int(limit))
        status = f"Papers fetched: {fetched}📌\nPDFs downloaded: {downloaded}⬇️"
        return status, pdfs
    except Exception:
        return f"{topic} research papers were not available", None


def summarize_ui():
    try:
        paper_text = call_funstion()
        os.makedirs("data/output", exist_ok=True)
        pdf_path = "data/output/synthesized_paper.pdf"
        text_to_pdf(paper_text, pdf_path)
        return paper_text, pdf_path
    except Exception as e:
        return f"Error during summarization:\n{str(e)}", None


def compare_ui():
    try:
        return compute_similarity()
    except Exception as e:
        return f"Error during comparison:\n{str(e)}"


# -------------------------
# Custom CSS — DARK ONLY
# -------------------------

custom_css = """
/* =========================
   APP BACKGROUND (DARK)
   ========================= */
body,
.gradio-container {
    # background: linear-gradient(90deg, #9febfc, #020617) !important;
    background: linear-gradient(90deg,#f4e5f0,#e536ab,#5c03bc,#0e0725) !important;
    font-family: "Segoe UI", Inter, sans-serif;
    overflow-x: hidden;
    overflow-y: auto;
}

/* =========================
   GLOBAL TEXT (FOR DARK BG)
   ========================= */
.markdown,
.markdown h1,
.markdown h2,
.markdown h3,
.markdown p {
    color: #f9fafb !important;
}

/* =========================
   SECTION CARDS
   ========================= */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 32px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    border-left: 10px solid transparent;
    position: relative;
    z-index: 1;
}

/* =========================
   STEP COLORS
   ========================= */
.step1 { background: #d1fae5; border-left-color: #16a34a; }
.step2 { background: #f9a87b; border-left-color: #f97d5b; }
.step3 { background: #e9d5ff; border-left-color: #7c3aed; }

.step1 button.primary { background: #16a34a !important; color: white !important; }
.step2 button.secondary { background: #f97d5b !important; color: white !important; }
.step3 button.stop { background: #7c3aed !important; color: white !important; }

/* =========================
   CARD TEXT
   ========================= */
.section-card h3 {
    color: #111827;
    font-weight: 700;
}

/* =========================
   LABELS — FORCE VISIBILITY
   ========================= */
label span,
.gr-label span,
.gr-form label span {
    color: #111827 !important;
    font-weight: 600;
}

/* =========================
   INPUTS
   ========================= */
input, textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
}

textarea::placeholder {
    color: #9ca3af;
}

/* =========================
   FILE UPLOAD
   ========================= */
.file {
    background: white !important;
    border: 1px dashed #c7d2fe !important;
}

/* =========================
   BUTTONS
   ========================= */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* =========================
   STAR BACKGROUND
   ========================= */
.stars {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
}

.star {
    position: absolute;
    color: rgba(255,255,255,1.0);
    font-size: 24px;
    animation: fall linear infinite;
}

@keyframes fall {
    0% { transform: translateY(-20vh); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(120vh); opacity: 0; }
}
"""

# -------------------------
# UI
# -------------------------

with gr.Blocks(
    title="PaperPilot AI",
    theme=gr.themes.Base(),
    css=custom_css,
) as demo:
    previous_pdfs = gr.State([])

    gr.HTML("""
    <div class="stars">
        <span class="star" style="left:5%;animation-duration:10s;animation-delay:-2s">✨</span>
        <span class="star" style="left:15%;animation-duration:14s;animation-delay:-6s">✦</span>
        <span class="star" style="left:25%;animation-duration:12s;animation-delay:-9s">✨</span>
        <span class="star" style="left:35%;animation-duration:16s;animation-delay:-4s">✧</span>
        <span class="star" style="left:45%;animation-duration:11s;animation-delay:-7s">✨</span>
        <span class="star" style="left:55%;animation-duration:13s;animation-delay:-3s">✦</span>
        <span class="star" style="left:65%;animation-duration:15s;animation-delay:-10s">✨</span>
        <span class="star" style="left:75%;animation-duration:12s;animation-delay:-5s">✧</span>
        <span class="star" style="left:85%;animation-duration:17s;animation-delay:-8s">✨</span>
        <span class="star" style="left:95%;animation-duration:14s;animation-delay:-6s">✦</span>
        <span class="star" style="left:5%;animation-duration:10s;animation-delay:-2s">✨</span>
        <span class="star" style="left:15%;animation-duration:14s;animation-delay:-6s">✦</span>
        <span class="star" style="left:25%;animation-duration:12s;animation-delay:-9s">✨</span>
        <span class="star" style="left:35%;animation-duration:16s;animation-delay:-4s">✧</span>
        <span class="star" style="left:45%;animation-duration:11s;animation-delay:-7s">✨</span>
        <span class="star" style="left:55%;animation-duration:13s;animation-delay:-3s">✦</span>
        <span class="star" style="left:65%;animation-duration:15s;animation-delay:-10s">✨</span>
        <span class="star" style="left:75%;animation-duration:12s;animation-delay:-5s">✧</span>
        <span class="star" style="left:85%;animation-duration:17s;animation-delay:-8s">✨</span>
        <span class="star" style="left:95%;animation-duration:14s;animation-delay:-6s">✦</span>
    </div>
    """)

    gr.Markdown("""
    # 🤖 PaperPilot AI  
    ### Automated Research Paper Discovery, Synthesis & Comparison
    """)

    gr.Markdown(
        "Fetch papers, generate a synthesized research draft, and compare documents using TF-IDF cosine similarity."
    )

    with gr.Column(elem_classes=["section-card", "step1"]):
        gr.Markdown("### Step 1: Fetch Research Papers")
        with gr.Row():
            topic_input = gr.Textbox(label="Research Topic", placeholder="e.g., Deepfake Detection")
            limit_input = gr.Number(label="Number of Papers", value=4, precision=0)

        run_btn = gr.Button("Fetch Papers", variant="primary")
        status_output = gr.Textbox(label="Status", lines=3)
        pdfs_output = gr.File(label="Downloaded Research PDFs", file_count="multiple")

        run_btn.click(run_pipeline_ui, [topic_input, limit_input], [status_output, pdfs_output])

    with gr.Column(elem_classes=["section-card", "step2"]):
        gr.Markdown("### Step 2: Generate Synthesized Paper")
        summarize_btn = gr.Button("Generate Summary", variant="secondary")

        summary_output = gr.Textbox(
            label="Synthesized Research Content",
            lines=20,
            placeholder="Generated research content will appear here..."
        )

        customization_input = gr.Textbox(
            label="Customization Instructions",
            placeholder="e.g., Elaborate the abstract or shorten the results section",
            lines=2
        )
        summary_pdf = gr.File(label="Download Synthesized Paper (PDF)", file_types=[".pdf"])

        summarize_btn.click(summarize_ui, None, [summary_output, summary_pdf])
        refine_btn = gr.Button("Refine Paper ✍️", variant="secondary")
        refine_btn.click(
            fn=refine_synthesized_paper,
            inputs=[summary_output, customization_input],
            outputs=[summary_output, summary_pdf]
        )

    with gr.Column(elem_classes=["section-card", "step3"]):
        gr.Markdown("### Step 3: Compare Papers")
        compare_btn = gr.Button("Compare Papers", variant="stop")

        compare_output = gr.Textbox(
            label="TF-IDF Cosine Similarity Results\nValues closer to 1 mean the papers are more similar.\nValues closer to 0 mean the papers are less similar.",
            lines=10,
            placeholder="Similarity results will appear here..."
        )

        compare_btn.click(compare_ui, None, compare_output)

demo.launch(share="True")
