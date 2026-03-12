import gradio as gr
import json
import os

def create_paper_viewer(session_id):
    """Create an interactive paper viewer with metadata"""
    
    def load_paper_list(session_id):
        """Load all fetched papers for this session"""
        metadata_dir = f"user_sessions/{session_id}/metadata"
        
        if not os.path.exists(metadata_dir):
            return []
        
        papers = []
        for filename in os.listdir(metadata_dir):
            if filename.endswith(".json"):
                with open(os.path.join(metadata_dir, filename), 'r', encoding='utf-8') as f:
                    papers.append(json.load(f))
        
        return papers
    
    def get_paper_choices(session_id):
        """Return dropdown choices for papers"""
        papers = load_paper_list(session_id)
        if not papers:
            return []
        return [f"{p['title']} ({p['year']})" for p in papers]
    
    def display_paper_details(selected_title, session_id):
        """Show paper metadata and PDF if available"""
        papers = load_paper_list(session_id)
        
        if not papers:
            return "No papers loaded", None, None
        
        # Find selected paper
        selected = None
        for p in papers:
            if f"{p['title']} ({p['year']})" == selected_title:
                selected = p
                break
        
        if not selected:
            return "Paper not found", None, None
        
        # Format metadata
        metadata_text = f"""
# {selected['title']}

**Authors:** {', '.join(selected['authors'])}

**Year:** {selected['year']}

**Paper ID:** {selected['paperId']}

**URL:** {selected['paper_url']}

---

**Abstract:**
{selected.get('abstract', 'No abstract available')}
"""
        
        # Check if PDF exists
        pdf_path = f"user_sessions/{session_id}/pdfs/{selected['paperId']}.pdf"
        
        if os.path.exists(pdf_path):
            return metadata_text, pdf_path, pdf_path
        else:
            return metadata_text, None, None
    
    return load_paper_list, get_paper_choices, display_paper_details