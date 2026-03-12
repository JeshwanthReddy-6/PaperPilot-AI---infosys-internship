import gradio as gr
from main import run_pipeline
from llm_drafting import call_function
from tf_idf import compute_similarity
from pdf_convert import text_to_pdf
from refine import refine_synthesized_paper
from utils import create_session_id, start_cleanup_scheduler, cleanup_old_sessions
import os
import json
import base64

# ===== AUTO CLEANUP ON STARTUP =====
print("🚀 Starting PaperPilot AI...")
cleanup_old_sessions(max_age_hours=2)
start_cleanup_scheduler(interval_minutes=30, max_age_hours=2)
# -------------------------
# Backend wrappers (NO CHANGES)
# -------------------------

paper_data_store = {}

def run_pipeline_ui(topic, limit, session_id):
    try:
        fetched, downloaded, pdfs = run_pipeline(topic, int(limit), session_id)
        
        metadata_dir = f"user_sessions/{session_id}/metadata"
        paper_choices = []
        
        paper_data_store.clear()
        
        for pdf_path in pdfs:
            paper_id = os.path.basename(pdf_path).replace('.pdf', '')
            meta_path = os.path.join(metadata_dir, f"{paper_id}.json")
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    display_name = f"{meta['title'][:50]}... ({meta['year']})"
                    paper_choices.append(display_name)
                    paper_data_store[display_name] = paper_id
        
        actual_downloaded = len(pdfs)
        status = f"Papers fetched: {fetched}📌\nPDFs downloaded: {actual_downloaded}⬇️"
        
        if actual_downloaded == 0:
            status += "\n⚠️ No open-access PDFs available for these papers."
        
        return (
            status, 
            pdfs,
            gr.update(choices=paper_choices, value=paper_choices[0] if paper_choices else None),
            gr.update(choices=paper_choices, value=paper_choices)
        )
    except Exception as e:
        return f"❌ Error: {str(e)}", None, gr.update(choices=[]), gr.update(choices=[], value=[])


def get_paper_id(selected_paper, session_id):
    paper_id = paper_data_store.get(selected_paper)
    
    if not paper_id:
        metadata_dir = f"user_sessions/{session_id}/metadata"
        if os.path.exists(metadata_dir):
            for filename in os.listdir(metadata_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(metadata_dir, filename), 'r') as f:
                        meta = json.load(f)
                        display_name = f"{meta['title'][:50]}... ({meta['year']})"
                        if display_name == selected_paper:
                            paper_id = meta['paperId']
                            paper_data_store[display_name] = paper_id
                            break
    return paper_id


def view_pdf_inline(selected_paper, session_id):
    if not selected_paper:
        return (
            "<div style='text-align: center; padding: 50px; background: #f0f9ff; border-radius: 12px; border: 2px dashed #3b82f6;'>"
            "<p style='font-size: 40px; margin: 0;'>📄</p>"
            "<p style='color: #1e40af; font-size: 16px; margin-top: 10px;'>Select a paper from the dropdown above</p>"
            "<p style='color: #3b82f6; font-size: 14px;'>Then click 'View PDF' to display it here</p>"
            "</div>", 
            None
        )
    
    try:
        paper_id = get_paper_id(selected_paper, session_id)
        
        if not paper_id:
            return (
                "<div style='text-align: center; padding: 50px; background: #fef2f2; border-radius: 12px; border: 2px solid #ef4444;'>"
                "<p style='font-size: 40px; margin: 0;'>❌</p>"
                "<p style='color: #dc2626; font-size: 16px;'>Paper not found</p>"
                "</div>", 
                None
            )
        
        pdf_path = f"user_sessions/{session_id}/pdfs/{paper_id}.pdf"
        
        if not os.path.exists(pdf_path):
            return (
                "<div style='text-align: center; padding: 50px; background: #fef2f2; border-radius: 12px; border: 2px solid #ef4444;'>"
                "<p style='font-size: 40px; margin: 0;'>❌</p>"
                "<p style='color: #dc2626; font-size: 16px;'>PDF file not found</p>"
                "</div>", 
                None
            )
        
        file_size = os.path.getsize(pdf_path)
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb > 2:
            html_content = f'''
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; border: 2px solid #f59e0b;">
                <p style="font-size: 60px; margin: 0;">📥</p>
                <p style="color: #92400e; font-size: 22px; font-weight: bold; margin: 15px 0;">Large PDF File</p>
                <p style="color: #a16207; font-size: 18px; margin: 10px 0;">
                    <strong>Size:</strong> {file_size_mb:.2f} MB
                </p>
                <div style="background: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <p style="color: #78350f; font-size: 14px; margin: 0;">
                        🔔 This file is too large to display in browser preview.
                    </p>
                </div>
                <p style="color: #92400e; font-size: 16px; font-weight: bold;">
                    👇 Please use the <span style="background: #fbbf24; padding: 3px 8px; border-radius: 5px;">"Download Selected PDF"</span> button below
                </p>
            </div>
            '''
            return html_content, pdf_path
        
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        html_content = f'''
        <div style="width: 100%; border: 2px solid #e5e7eb; border-radius: 12px; overflow: hidden; background: white;">
            <div style="padding: 10px 15px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">📄 PDF Viewer</span>
                <span style="font-size: 12px; background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 10px;">Size: {file_size_mb:.2f} MB</span>
            </div>
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}#toolbar=1&navpanes=1" 
                width="100%" 
                height="650px" 
                style="border: none;"
            >
            </iframe>
        </div>
        '''
        return html_content, pdf_path
            
    except Exception as e:
        return (
            f"<div style='text-align: center; padding: 50px; background: #fef2f2; border-radius: 12px; border: 2px solid #ef4444;'>"
            f"<p style='font-size: 40px; margin: 0;'>❌</p>"
            f"<p style='color: #dc2626; font-size: 16px;'>Error: {str(e)}</p>"
            f"</div>", 
            None
        )


def get_paper_info(selected_paper, session_id):
    if not selected_paper:
        return "Select a paper to view its details"
    
    try:
        paper_id = get_paper_id(selected_paper, session_id)
        
        if not paper_id:
            return "Paper not found"
        
        meta_path = f"user_sessions/{session_id}/metadata/{paper_id}.json"
        pdf_path = f"user_sessions/{session_id}/pdfs/{paper_id}.pdf"
        
        pdf_status = "❌ PDF Not Found"
        if os.path.exists(pdf_path):
            size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            pdf_status = f"✅ PDF Available ({size_mb:.2f} MB)"
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            
            info = f"""
### 📄 {meta['title']}

**Authors:** {', '.join(meta['authors'])}

**Year:** {meta['year']}

**Status:** {pdf_status}

**Link:** [View on Semantic Scholar]({meta['paper_url']})
"""
            return info
        return "Paper metadata not found"
    except Exception as e:
        return f"Error: {str(e)}"


def select_all_papers(choices):
    if choices is None or len(choices) == 0:
        return gr.update(value=[])
    return gr.update(value=choices)


def deselect_all_papers():
    return gr.update(value=[])


def get_selection_display(selected_papers, all_choices):
    if all_choices is None or len(all_choices) == 0:
        return "<p style='color: #6b7280; text-align: center;'>No papers available. Please fetch papers first.</p>"
    
    if selected_papers is None:
        selected_papers = []
    
    html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
    
    for paper in all_choices:
        is_selected = paper in selected_papers
        
        if is_selected:
            html += f'''
            <div style="display: flex; align-items: center; padding: 12px 15px; background: linear-gradient(90deg, #dcfce7, #bbf7d0); border-radius: 10px; border: 2px solid #22c55e;">
                <span style="font-size: 20px; margin-right: 12px;">✅</span>
                <span style="color: #166534; font-weight: 500;">{paper}</span>
                <span style="margin-left: auto; background: #22c55e; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px;">SELECTED</span>
            </div>
            '''
        else:
            html += f'''
            <div style="display: flex; align-items: center; padding: 12px 15px; background: #f9fafb; border-radius: 10px; border: 2px solid #e5e7eb;">
                <span style="font-size: 20px; margin-right: 12px;">⬜</span>
                <span style="color: #6b7280;">{paper}</span>
                <span style="margin-left: auto; background: #e5e7eb; color: #6b7280; padding: 3px 10px; border-radius: 15px; font-size: 12px;">NOT SELECTED</span>
            </div>
            '''
    
    html += "</div>"
    
    selected_count = len(selected_papers)
    total_count = len(all_choices)
    
    html += f'''
    <div style="margin-top: 15px; padding: 12px; background: linear-gradient(90deg, #eff6ff, #dbeafe); border-radius: 10px; text-align: center;">
        <span style="color: #1e40af; font-weight: bold; font-size: 16px;">
            📊 {selected_count} of {total_count} papers selected for synthesis
        </span>
    </div>
    '''
    
    return html


def summarize_ui(selected_papers, session_id):
    try:
        if selected_papers is None or len(selected_papers) == 0:
            return (
                "<p style='color: #ef4444; padding: 20px;'>❌ Please select at least one paper to summarize.</p>", 
                "",  # raw text
                None  # pdf
            )
        
        if isinstance(selected_papers, str):
            selected_papers = [selected_papers]
        
        selected_paper_ids = []
        
        for paper in selected_papers:
            paper_id = get_paper_id(paper, session_id)
            if paper_id:
                selected_paper_ids.append(paper_id)
        
        if len(selected_paper_ids) == 0:
            return (
                "<p style='color: #ef4444; padding: 20px;'>❌ Could not find selected papers. Please try fetching papers again.</p>",
                "",
                None
            )
        
        paper_count = len(selected_paper_ids)
        
        paper_text = call_function(session_id, selected_paper_ids)
        
        output_dir = f"user_sessions/{session_id}/output"
        os.makedirs(output_dir, exist_ok=True)
        pdf_path = f"{output_dir}/synthesized_paper.pdf"
        text_to_pdf(paper_text, pdf_path)
        
        # Format for display
        formatted_html = format_paper_for_display(paper_text, paper_count)
        
        return formatted_html, paper_text, pdf_path
    except Exception as e:
        return (
            f"<p style='color: #ef4444; padding: 20px;'>❌ Error during summarization: {str(e)}</p>",
            "",
            None
        )


def compare_ui(session_id):
    try:
        return compute_similarity(session_id)
    except Exception as e:
        return f"Error during comparison:\n{str(e)}"


def refine_ui(raw_paper_text, instruction, session_id):
    try:
        if not raw_paper_text or raw_paper_text.strip() == "":
            return (
                "<p style='color: #ef4444; padding: 20px;'>❌ No paper to refine. Please generate a synthesis first.</p>",
                "",
                None
            )
        
        refined_text, pdf_path = refine_synthesized_paper(raw_paper_text, instruction, session_id)
        
        # Format for display
        formatted_html = format_paper_for_display(refined_text, "refined")
        
        return formatted_html, refined_text, pdf_path
    except Exception as e:
        return (
            f"<p style='color: #ef4444; padding: 20px;'>❌ Error: {str(e)}</p>",
            "",
            None
        )

def format_paper_for_display(paper_text, paper_count):
    """Convert plain text paper to styled HTML for display"""
    if not paper_text or paper_text.startswith("❌"):
        return paper_text
    
    lines = paper_text.strip().split('\n')
    html_output = f"""
    <div style="background: white; padding: 30px; border-radius: 12px; border: 2px solid #e5e7eb; font-family: 'Georgia', serif; line-height: 1.8;">
        <div style="text-align: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px solid #3b82f6;">
            <span style="background: #dbeafe; color: #1e40af; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; font-family: sans-serif;">
                📊 Synthesized from {paper_count} selected paper(s)
            </span>
        </div>
    """
    
    is_title = True
    current_section = None
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            html_output += "<br>"
            continue
        
        # Check for section headers
        if stripped in ["Abstract", "Methods", "Results", "References"]:
            html_output += f"""
            <h2 style="color: #1e293b; font-size: 1.5rem; font-weight: 700; margin: 25px 0 15px 0; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb; text-align: left;">
                {stripped}
            </h2>
            """
            current_section = stripped
            is_title = False
        elif is_title and len(stripped) > 5 and not stripped.startswith("Abstract"):
            # First non-empty line is the title
            html_output += f"""
            <h1 style="color: #0f172a; font-size: 1.8rem; font-weight: 800; text-align: center; margin: 20px 0 30px 0;">
                {stripped}
            </h1>
            """
            is_title = False
        else:
            # Regular paragraph
            html_output += f"""
            <p style="color: #334155; font-size: 1rem; margin: 10px 0; text-align: justify;">
                {stripped}
            </p>
            """
    
    html_output += "</div>"
    return html_output


# -------------------------
# ENHANCED CUSTOM CSS
# -------------------------

custom_css = """
/* ===== GLOBAL STYLES ===== */
body,
.gradio-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    min-height: 100vh;
}

/* ===== HEADER STYLES ===== */
.main-header {
    text-align: center;
    padding: 40px 20px;
    margin-bottom: 30px;
}

.main-header h1 {
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #00d4ff, #7b2cbf, #ff6b6b, #feca57);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    text-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
}

.main-header .subtitle {
    font-size: 1.3rem;
    color: #a0aec0;
    margin-top: 10px;
    font-weight: 400;
}

.main-header .tagline {
    font-size: 1rem;
    color: #718096;
    margin-top: 15px;
    padding: 10px 25px;
    background: rgba(255,255,255,0.05);
    border-radius: 30px;
    display: inline-block;
    border: 1px solid rgba(255,255,255,0.1);
}

/* ===== SECTION CARDS ===== */
.section-card {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin-bottom: 25px !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
    border: none !important;
    position: relative;
    overflow: hidden;
}

.section-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
}

.step1::before { background: linear-gradient(90deg, #10b981, #34d399); }
.step2::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.step3::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.step4::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

/* ===== STEP HEADERS ===== */
.step-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f1f5f9;
}

.step-number {
    width: 45px;
    height: 45px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}

.step1 .step-number { background: linear-gradient(135deg, #10b981, #059669); }
.step2 .step-number { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.step3 .step-number { background: linear-gradient(135deg, #f59e0b, #d97706); }
.step4 .step-number { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }

.step-title {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #1e293b !important;
    margin: 0 !important;
}

.step-description {
    font-size: 0.9rem;
    color: #64748b;
    margin: 0;
}

/* ===== FORM ELEMENTS ===== */
label span {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

input, textarea, select {
    background: #f8fafc !important;
    color: #1e293b !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* ===== BUTTONS ===== */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    border: none !important;
}

button.primary {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5) !important;
}

button.secondary {
    background: linear-gradient(135deg, #f1f5f9, #e2e8f0) !important;
    color: #475569 !important;
}

button.secondary:hover {
    background: linear-gradient(135deg, #e2e8f0, #cbd5e1) !important;
    transform: translateY(-1px) !important;
}

button.stop {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
}

/* ===== DROPDOWN ===== */
.gr-dropdown {
    border-radius: 12px !important;
}

/* ===== FILE COMPONENTS ===== */
.gr-file {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
}

/* ===== MARKDOWN IN CARDS ===== */
.section-card .markdown p,
.section-card .markdown span {
    color: #475569 !important;
}

.section-card .markdown h3 {
    color: #1e293b !important;
}

/* ===== STARS ANIMATION ===== */
.stars {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.star {
    position: absolute;
    color: rgba(255, 255, 255, 0.8);
    font-size: 20px;
    animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2.5rem !important;
    }
    
    .section-card {
        padding: 20px !important;
    }
}

/* ===== FOOTER ===== */
.footer {
    text-align: center;
    padding: 30px;
}
"""

# -------------------------
# UI LAYOUT
# -------------------------

with gr.Blocks(
    title="PaperPilot AI | Smart Research Assistant",
    theme=gr.themes.Base(),
    css=custom_css,
) as demo:
    
    session_id = gr.State(value=create_session_id)
    current_paper_choices = gr.State(value=[])

    # ===== ANIMATED BACKGROUND =====
    gr.HTML("""
    <div class="stars">
        <span class="star" style="left: 5%; top: 10%; animation-delay: 0s;">✦</span>
        <span class="star" style="left: 15%; top: 30%; animation-delay: 0.5s;">✧</span>
        <span class="star" style="left: 25%; top: 15%; animation-delay: 1s;">✦</span>
        <span class="star" style="left: 35%; top: 45%; animation-delay: 1.5s;">✧</span>
        <span class="star" style="left: 45%; top: 20%; animation-delay: 2s;">✦</span>
        <span class="star" style="left: 55%; top: 35%; animation-delay: 0.3s;">✧</span>
        <span class="star" style="left: 65%; top: 10%; animation-delay: 0.8s;">✦</span>
        <span class="star" style="left: 75%; top: 40%; animation-delay: 1.3s;">✧</span>
        <span class="star" style="left: 85%; top: 25%; animation-delay: 1.8s;">✦</span>
        <span class="star" style="left: 92%; top: 50%; animation-delay: 0.6s;">✧</span>
        <span class="star" style="left: 10%; top: 60%; animation-delay: 2.2s;">✦</span>
        <span class="star" style="left: 30%; top: 70%; animation-delay: 0.9s;">✧</span>
        <span class="star" style="left: 50%; top: 65%; animation-delay: 1.6s;">✦</span>
        <span class="star" style="left: 70%; top: 75%; animation-delay: 2.5s;">✧</span>
        <span class="star" style="left: 90%; top: 68%; animation-delay: 1.1s;">✦</span>
    </div>
    
    <div style="position: fixed; top: -100px; left: -100px; width: 300px; height: 300px; background: radial-gradient(circle, rgba(59,130,246,0.3) 0%, transparent 70%); border-radius: 50%; filter: blur(40px); z-index: 0;"></div>
    <div style="position: fixed; bottom: -100px; right: -100px; width: 400px; height: 400px; background: radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%); border-radius: 50%; filter: blur(40px); z-index: 0;"></div>
    """)

    # ===== MAIN HEADER =====
    gr.HTML("""
    <div class="main-header">
        <h1>🤖 PaperPilot AI</h1>
        <p class="subtitle">Your Intelligent Research Paper Assistant</p>
        <p class="tagline">🔍 Discover  •  📄 Synthesize  •  📊 Compare</p>
    </div>
    """)

    # ===== STEP 1: FETCH PAPERS =====
    with gr.Column(elem_classes=["section-card", "step1"]):
        gr.HTML("""
        <div class="step-header">
            <div class="step-number">1</div>
            <div>
                <h3 class="step-title">Fetch Research Papers</h3>
                <p class="step-description">Search and download academic papers from Semantic Scholar</p>
            </div>
        </div>
        """)
        
        with gr.Row():
            topic_input = gr.Textbox(
                label="🔎 Research Topic", 
                placeholder="e.g., Deepfake Detection, Machine Learning, Climate Change...",
                scale=3
            )
            limit_input = gr.Number(
                label="📚 Number of Papers", 
                value=4, 
                precision=0,
                scale=1
            )

        gr.HTML("""
        <div style="background: linear-gradient(135deg, #dbeafe, #bfdbfe); border: 2px solid #3b82f6; border-radius: 12px; padding: 12px 15px; margin: 10px 0;">
            <p style="margin: 0; color: #1e40af; font-size: 0.9rem;">
                💡 <strong>Tip:</strong> Not all papers have open-access PDFs. 
                <span style="background: #1e40af; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem;">Increase the number of papers</span> 
                to get more downloadable results!
            </p>
        </div>
        """)

        run_btn = gr.Button("🚀 Fetch Papers", variant="primary")
        status_output = gr.Textbox(label="📋 Status", lines=3)

    # ===== STEP 2: VIEW & DOWNLOAD =====
    with gr.Column(elem_classes=["section-card", "step2"]):
        gr.HTML("""
        <div class="step-header">
            <div class="step-number">2</div>
            <div>
                <h3 class="step-title">View & Download PDFs</h3>
                <p class="step-description">Preview papers in browser or download them</p>
            </div>
        </div>
        """)
        
        paper_selector = gr.Dropdown(
            label="📑 Select a Paper to View",
            choices=[],
            interactive=True
        )
        
        view_btn = gr.Button("👁️ View PDF", variant="secondary")
        paper_info = gr.Markdown("*Select a paper to view its details*")
        
        pdf_viewer_html = gr.HTML(
            value="""
            <div style='text-align: center; padding: 60px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; border: 2px dashed #3b82f6;'>
                <p style='font-size: 50px; margin: 0;'>📄</p>
                <p style='color: #1e40af; font-size: 18px; font-weight: 600; margin-top: 15px;'>PDF Preview Area</p>
                <p style='color: #3b82f6; font-size: 14px;'>Select a paper and click 'View PDF'</p>
            </div>
            """
        )
        
        gr.HTML("<div style='height: 20px;'></div>")
        gr.HTML("<p style='color: #475569; font-weight: 600; font-size: 1rem;'>📥 Download Options</p>")
        
        with gr.Row():
            single_pdf_download = gr.File(label="Download Selected PDF", file_count="single")
            all_pdfs_output = gr.File(label="Download All PDFs", file_count="multiple")
        
        view_btn.click(
            view_pdf_inline,
            [paper_selector, session_id],
            [pdf_viewer_html, single_pdf_download]
        )
        
        paper_selector.change(
            get_paper_info,
            [paper_selector, session_id],
            paper_info
        )

    # ===== STEP 3: SYNTHESIZE =====
    # ===== STEP 3: SYNTHESIZE =====
    with gr.Column(elem_classes=["section-card", "step3"]):
        gr.HTML("""
        <div class="step-header">
            <div class="step-number">3</div>
            <div>
                <h3 class="step-title">Generate Synthesized Paper</h3>
                <p class="step-description">AI-powered synthesis of selected research papers</p>
            </div>
        </div>
        """)
        
        gr.HTML("<p style='color: #64748b; font-size: 0.9rem; margin-bottom: 15px;'>👆 Click the checkboxes to select/deselect papers for synthesis</p>")
        
        papers_to_summarize = gr.CheckboxGroup(
            label="📝 Select Papers to Include",
            choices=[],
            value=[],
            interactive=True
        )
        
        with gr.Row():
            select_all_btn = gr.Button("✅ Select All")
            deselect_all_btn = gr.Button("❌ Clear All")
        
        selection_display = gr.HTML(
            value="<p style='color: #6b7280; text-align: center; padding: 20px;'>No papers available yet. Fetch papers first.</p>"
        )
        
        def update_display(selected, choices):
            return get_selection_display(selected, choices)
        
        papers_to_summarize.change(
            update_display,
            [papers_to_summarize, current_paper_choices],
            [selection_display]
        )
        
        summarize_btn = gr.Button("🤖 Generate Synthesis", variant="primary")

        # Styled HTML display for the paper
        summary_display = gr.HTML(
            value="<div style='padding: 40px; text-align: center; color: #6b7280; background: #f9fafb; border-radius: 12px; border: 2px dashed #e5e7eb;'><p style='font-size: 40px; margin: 0;'>📝</p><p>Your synthesized research paper will appear here...</p></div>"
        )
        
        # Hidden textbox to store raw text for refinement
        raw_paper_text = gr.Textbox(visible=False)

        gr.HTML("""
        <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border: 2px solid #f59e0b; border-radius: 12px; padding: 15px; margin: 15px 0;">
            <p style="margin: 0 0 8px 0; color: #92400e; font-weight: 600; font-size: 0.95rem;">✏️ Refinement Instructions (Optional)</p>
            <p style="margin: 0; color: #a16207; font-size: 0.85rem;">Want to customize the generated paper? Enter your instructions below:</p>
        </div>
        """)

        customization_input = gr.Textbox(
            label="",
            placeholder="e.g., Make the abstract more detailed, add more technical depth, focus on methodology...",
            lines=2
        )
        
        refine_btn = gr.Button("✨ Refine Paper", variant="secondary")
        
        summary_pdf = gr.File(label="📄 Download as PDF", file_types=[".pdf"])

        summarize_btn.click(
            summarize_ui, 
            [papers_to_summarize, session_id], 
            [summary_display, raw_paper_text, summary_pdf]
        )
        
        refine_btn.click(
            fn=refine_ui,
            inputs=[raw_paper_text, customization_input, session_id],
            outputs=[summary_display, raw_paper_text, summary_pdf]
        )
    # ===== STEP 4: COMPARE =====
    with gr.Column(elem_classes=["section-card", "step4"]):
        gr.HTML("""
        <div class="step-header">
            <div class="step-number">4</div>
            <div>
                <h3 class="step-title">Compare Papers</h3>
                <p class="step-description">Analyze similarity between papers using TF-IDF</p>
            </div>
        </div>
        """)
        
        gr.HTML("""
        <div style="background: linear-gradient(135deg, #f3e8ff, #e9d5ff); border: 2px solid #8b5cf6; border-radius: 12px; padding: 15px; margin-bottom: 15px;">
            <p style="margin: 0 0 10px 0; color: #5b21b6; font-weight: 600; font-size: 1rem;">📊 Understanding Similarity Scores</p>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; background: white; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #22c55e;">
                    <p style="margin: 0; color: #166534; font-weight: 600;">Score close to 1.0</p>
                    <p style="margin: 5px 0 0 0; color: #15803d; font-size: 0.85rem;">📗 Papers are <strong>very similar</strong></p>
                </div>
                <div style="flex: 1; min-width: 200px; background: white; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <p style="margin: 0; color: #dc2626; font-weight: 600;">Score close to 0.0</p>
                    <p style="margin: 5px 0 0 0; color: #b91c1c; font-size: 0.85rem;">📕 Papers are <strong>very different</strong></p>
                </div>
            </div>
        </div>
        """)
        
        compare_btn = gr.Button("📊 Analyze Similarity", variant="stop")

        compare_output = gr.Textbox(
            label="📈 Similarity Analysis Results",
            lines=10,
            placeholder="Similarity comparison results will appear here..."
        )

        compare_btn.click(
            compare_ui, 
            [session_id], 
            compare_output
        )

    # ===== FOOTER =====
        # ===== FOOTER =====
    gr.HTML("""
    <div style="text-align: center; padding: 30px; margin-top: 20px;">
        <div style="display: inline-flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.1); padding: 12px 25px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.2);">
            <span style="font-size: 24px;">🤖</span>
            <span style="font-size: 1.1rem; font-weight: 600; background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PaperPilot AI</span>
        </div>
    </div>
    """)

    # ===== CONNECT FETCH BUTTON =====
    def fetch_and_store(topic, limit, session_id):
        status, pdfs, dropdown_update, checkbox_update = run_pipeline_ui(topic, limit, session_id)
        choices = checkbox_update.get("choices", []) if isinstance(checkbox_update, dict) else []
        initial_display = get_selection_display(choices, choices)
        return status, pdfs, dropdown_update, checkbox_update, choices, initial_display
    
    run_btn.click(
        fetch_and_store, 
        [topic_input, limit_input, session_id], 
        [status_output, all_pdfs_output, paper_selector, papers_to_summarize, current_paper_choices, selection_display]
    )
    
    select_all_btn.click(
        select_all_papers,
        [current_paper_choices],
        [papers_to_summarize]
    ).then(
        update_display,
        [papers_to_summarize, current_paper_choices],
        [selection_display]
    )
    
    deselect_all_btn.click(
        deselect_all_papers,
        [],
        [papers_to_summarize]
    ).then(
        lambda choices: get_selection_display([], choices),
        [current_paper_choices],
        [selection_display]
    )

demo.launch(share=True)