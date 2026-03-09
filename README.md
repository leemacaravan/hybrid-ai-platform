# 🤖 Hybrid AI Platform

A multi-agent AI platform built with Ollama, ChromaDB, and CrewAI. Runs 100% locally — no data leaves your machine.

## Features

### 🎯 Career Co-Pilot
- Paste any job description → 4 agents analyze, gap-check, rewrite your resume bullets, and generate interview questions
- RAG-powered: searches your personal experience database for the most relevant content

### 🚨 Missing Persons Intelligence
- Paste any unstructured case report or witness tip → extracts structured data, cross-references against all cases, generates investigator brief + family communication
- Semantic cross-referencing: finds matches by meaning, not just keywords

### 📄 LaTeX Resume Editor
- Upload your resume ZIP (.tex + .cls + assets) + job description → AI edits your resume
- Confidence scores per change (🟢 High / 🟡 Medium / 🔴 Low)
- Never touches URLs, dates, or company names
- Downloads an Overleaf-ready ZIP

## Setup

```bash
# 1. Install Ollama from https://ollama.com
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Clone and install
git clone https://github.com/leemacaravan/hybrid-ai-platform
cd hybrid-ai-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. Run
python -m ui.app
```

Open http://127.0.0.1:7860

## Stack
- **LLM**: Ollama (llama3.2) — local, free, private
- **Embeddings**: nomic-embed-text
- **Vector DB**: ChromaDB
- **Memory**: SQLite
- **Agents**: CrewAI
- **UI**: Gradio
- **Scraping**: BeautifulSoup4 + Playwright

## Project Structure
```
hybrid-ai-platform/
├── core/               # Shared: embeddings, vectorstore, memory
├── career/             # Career Co-Pilot agents + LaTeX editor
├── missing_persons/    # Missing Persons Intelligence agents
├── ui/                 # Gradio interface
└── requirements.txt
```
