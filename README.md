
# 🧠 AI Research Agent

## Overview
AI Research Agent is a tool designed to automate the process of collecting, analyzing, and summarizing academic research papers.  
Users provide a **topic name** and the **number of papers** they want, and the system fetches relevant papers from [Semantic Scholar](https://www.semanticscholar.org/).  
The agent then extracts key findings, summarizes them using a LLaMA model via the Groq API, and produces a downloadable **APA-formatted summarized research paper**.

---

## ✨ Features
- 🔍 Fetch research papers from Semantic Scholar based on user input.
- 📄 Extract full text and identify **key findings** using phrases like:
  - *"we propose"*
  - *"we introduce"*
  - *"our approach"*
  - *"our method"*
  - *"we demonstrate"*
  - *"outperforms"*
- 🤖 Summarize findings using LLaMA model through Groq API.
- 📑 Generate a **summarized research paper** in APA format.
- 🎨 Customization options:
  - Elaborate or refine the abstract.
  - Edit or change the title.
  - Adjust sections for clarity or emphasis.
- 💾 Download the final summarized paper.
- 🔗 Compare research papers pairwise by calculating **cosine similarity scores** to measure content overlap. 
---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Access to Groq API
- Semantic Scholar API key (if required)
- Git

### Installation

You don’t need to pre-install every dependency manually.  
Just run the project, and whenever the terminal asks for a missing package or library, install it as prompted.

Steps:
```bash
# Clone the repository
git clone https://github.com/springboardmentor23/ai_research_agent.git

# Navigate into the project folder
cd ai_research_agent

# Run the UI

python ui.py

