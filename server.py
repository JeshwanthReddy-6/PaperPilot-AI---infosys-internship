from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid

# Import your existing modules
from main import run_pipeline
from llm_drafting import call_function
from tf_idf import compute_similarity
from refine import refine_synthesized_paper
from utils import create_session_id, cleanup_old_sessions, start_cleanup_scheduler

# Initialize FastAPI
app = FastAPI(title="PaperPilot AI", version="2.0")

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Startup: Clean old sessions and start scheduler
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting PaperPilot AI...")
    cleanup_old_sessions(max_age_hours=2)
    start_cleanup_scheduler(interval_minutes=30, max_age_hours=2)
    print("✅ Server ready!")

# ===== Pydantic Models =====

class FetchRequest(BaseModel):
    topic: str
    limit: int
    session_id: str

class SynthesizeRequest(BaseModel):
    selected_papers: List[str]
    session_id: str

class RefineRequest(BaseModel):
    instruction: str
    session_id: str

class CompareRequest(BaseModel):
    session_id: str

# ===== Helper Functions =====

def get_paper_metadata(session_id: str, paper_id: str):
    """Load metadata for a specific paper"""
    meta_path = f"user_sessions/{session_id}/metadata/{paper_id}.json"
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_all_papers(session_id: str):
    """Get list of all valid downloadable papers for a session"""
    metadata_dir = f"user_sessions/{session_id}/metadata"
    if not os.path.exists(metadata_dir):
        return []
    
    papers = []
    for filename in os.listdir(metadata_dir):
        if filename.endswith(".json"):
            with open(os.path.join(metadata_dir, filename), 'r', encoding='utf-8') as f:
                meta = json.load(f)

                pdf_exists = os.path.exists(
                    f"user_sessions/{session_id}/pdfs/{meta['paperId']}.pdf"
                )

                # Only include papers that really have downloadable/viewable PDFs
                if pdf_exists:
                    papers.append({
                        "id": meta["paperId"],
                        "title": meta["title"],
                        "authors": meta["authors"],
                        "year": meta["year"],
                        "url": meta["paper_url"],
                        "has_pdf": True
                    })
    return papers

def format_paper_for_display(paper_text: str, paper_count):
    """Convert plain text paper to HTML with styling"""
    if not paper_text or paper_text.startswith("❌"):
        return paper_text
    
    lines = paper_text.strip().split('\n')
    html_output = f"""
    <div class="paper-display">
        <div class="paper-badge">
            📊 Synthesized from {paper_count} selected paper(s)
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
            html_output += f'<h2 class="paper-section-header">{stripped}</h2>'
            current_section = stripped
            is_title = False
        elif is_title and len(stripped) > 5 and not stripped.startswith("Abstract"):
            # First non-empty line is the title
            html_output += f'<h1 class="paper-title">{stripped}</h1>'
            is_title = False
        else:
            # Regular paragraph
            html_output += f'<p class="paper-paragraph">{stripped}</p>'
    
    html_output += "</div>"
    return html_output

# ===== Routes =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    session_id = str(uuid.uuid4())
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_id": session_id
    })

@app.post("/api/fetch-papers")
async def fetch_papers(data: FetchRequest):
    """Fetch papers from Semantic Scholar"""
    try:
        fetched, downloaded, pdfs = run_pipeline(data.topic, data.limit, data.session_id)
        
        papers = get_all_papers(data.session_id)
        
        return JSONResponse({
            "success": True,
            "fetched": fetched,
            "downloaded": downloaded,
            "papers": papers,
            "message": f"✅ Fetched {fetched} papers, downloaded {downloaded} PDFs"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/papers/{session_id}")
async def get_papers(session_id: str):
    """Get all papers for a session"""
    try:
        papers = get_all_papers(session_id)
        return JSONResponse({
            "success": True,
            "papers": papers
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/pdf/{session_id}/{paper_id}")
async def get_pdf(session_id: str, paper_id: str):
    """Stream PDF file"""
    pdf_path = f"user_sessions/{session_id}/pdfs/{paper_id}.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={paper_id}.pdf"
        }
    )

@app.get("/api/paper-metadata/{session_id}/{paper_id}")
async def get_paper_metadata_route(session_id: str, paper_id: str):
    """Get metadata for a specific paper"""
    meta = get_paper_metadata(session_id, paper_id)
    if meta:
        return JSONResponse({
            "success": True,
            "metadata": meta
        })
    else:
        return JSONResponse({
            "success": False,
            "error": "Metadata not found"
        }, status_code=404)

@app.post("/api/synthesize")
async def synthesize_papers(data: SynthesizeRequest):
    """Generate synthesized paper from selected papers"""
    try:
        if not data.selected_papers or len(data.selected_papers) == 0:
            return JSONResponse({
                "success": False,
                "error": "Please select at least one paper"
            }, status_code=400)
        
        # The selected_papers now contains paper IDs directly from the frontend
        paper_ids = data.selected_papers
        
        # You might want to add a check here if these paper_ids actually exist
        # and belong to the current session, though main.py will handle if
        # it can't find content for them.

        if len(paper_ids) == 0: # This might happen if selected_papers is empty after filtering for valid IDs (not needed if frontend sends valid IDs)
             return JSONResponse({
                "success": False,
                "error": "No valid papers selected for synthesis."
            }, status_code=400)
        
        # Generate synthesis
        paper_text = call_function(data.session_id, paper_ids)
        
        # Format for display
        formatted_html = format_paper_for_display(paper_text, len(paper_ids))
        
        return JSONResponse({
            "success": True,
            "paper_html": formatted_html,
            "paper_text": paper_text,
            "message": f"✅ Generated synthesis from {len(paper_ids)} paper(s)"
        })
    except Exception as e:
        import traceback
        traceback.print_exc() # This will print the full error stack to your server console
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/refine")
async def refine_paper(data: RefineRequest):
    """Refine the synthesized paper"""
    try:
        # Load existing synthesized paper
        output_dir = f"user_sessions/{data.session_id}/output"
        text_path = f"{output_dir}/synthesized_paper.txt"
        
        if not os.path.exists(text_path):
            return JSONResponse({
                "success": False,
                "error": "No synthesized paper found. Please generate one first."
            }, status_code=400)
        
        with open(text_path, 'r', encoding='utf-8') as f:
            existing_paper = f.read()
        
        # Refine it
        refined_text, pdf_path = refine_synthesized_paper(
            existing_paper,
            data.instruction,
            data.session_id
        )
        
        # Update the text file
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(refined_text)
        
        # Format for display
        formatted_html = format_paper_for_display(refined_text, "refined")
        
        return JSONResponse({
            "success": True,
            "paper_html": formatted_html,
            "paper_text": refined_text,
            "message": "✅ Paper refined successfully"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/compare")
async def compare_papers(data: CompareRequest):
    """Compare papers using TF-IDF"""
    try:
        result = compute_similarity(data.session_id)
        return JSONResponse({
            "success": True,
            "result": result
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/download-synthesis/{session_id}")
async def download_synthesis(session_id: str):
    """Download synthesized paper as PDF"""
    pdf_path = f"user_sessions/{session_id}/output/synthesized_paper.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Synthesized paper not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="PaperPilot_AI_Synthesis.pdf",
        headers={
            "Content-Disposition": "attachment; filename=PaperPilot_AI_Synthesis.pdf"
        }
    )

@app.get("/api/download-pdf/{session_id}/{paper_id}")
async def download_single_pdf(session_id: str, paper_id: str):
    """Download a single paper PDF"""
    pdf_path = f"user_sessions/{session_id}/pdfs/{paper_id}.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Get paper title for filename
    meta = get_paper_metadata(session_id, paper_id)
    if meta:
        filename = f"{meta['title'][:50].replace(' ', '_')}.pdf"
    else:
        filename = f"{paper_id}.pdf"
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# Run server (for local testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)