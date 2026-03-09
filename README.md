# 🤖 Hybrid AI Platform

> A full-stack, multi-agent AI platform built by a CS senior — running 100% locally, no data ever leaves your machine.

Built with **Ollama** (local LLM) + **ChromaDB** (vector RAG) + **CrewAI** (agent orchestration) + **Gradio** (UI). Two completely independent use cases share one intelligent core infrastructure.

---

## 🚦 Current Build Status

| Feature | Status | Notes |
|---|---|---|
| Shared Core (RAG + Memory) | ✅ Complete | ChromaDB + nomic embeddings + SQLite |
| Career Co-Pilot (4 agents) | ✅ Complete | Job scraper, gap analyzer, resume rewriter, interview prepper |
| Missing Persons Intelligence (4 agents) | ✅ Complete | Extractor, cross-referencer, report generator, family updater |
| LaTeX Resume Editor | ✅ Complete | ZIP upload → AI edits → Overleaf-ready ZIP download |
| Job URL Scraper | ✅ Complete | Indeed, Glassdoor, generic URLs (LinkedIn workaround included) |
| Gradio UI (4 tabs) | ✅ Complete | Career, Missing Persons, LaTeX Editor, About |
| PDF Resume Upload | 🔜 Next | Load PDF resume into RAG database |
| Job Application Tracker | 🔜 Next | Track applications, statuses, match scores |
| Suggestion Engine | 🔜 Next | Project ideas, seniority reframes, metrics, open source, 30-day plan |
| Follow-up Chat Agent | 🔜 Next | Ask follow-up questions after resume edits |
| Public Deployment | 🔜 Planned | Hugging Face Spaces or VPS |

---

## ✨ Why This Project Is Impressive

This isn't a ChatGPT wrapper. Here's what's actually happening under the hood:

### 🧠 Real RAG (Retrieval-Augmented Generation)
Your resume experience is chunked, embedded into vectors using `nomic-embed-text`, and stored in ChromaDB. When you apply to a job, the system **semantically searches your experience** — not by keywords, but by *meaning* — and retrieves the most relevant bullets before passing them to the LLM. This is the #1 most asked-about AI architecture in engineering interviews right now.

### 🤖 Multi-Agent Orchestration
Each pipeline runs **4 specialized AI agents in sequence**, where each agent's output becomes the next agent's input. This is the same pattern used in production AI systems at companies like Salesforce, DocuSign, and PwC. Built from scratch using CrewAI.

### 🔒 100% Local & Private
Everything runs on your machine via Ollama. No API keys, no cloud calls, no data sent anywhere. This is especially critical for the Missing Persons side — sensitive case data never leaves the device.

### 🏥 Real-World Impact
The Missing Persons Intelligence system was built in collaboration with a real patient-tracking application. A vague anonymous witness tip can be cross-referenced against all open cases using semantic similarity — matching people by description, not just name. That's a capability most law enforcement tools don't have.

### 📄 LaTeX-Aware Resume Editing
The resume editor understands LaTeX syntax — it edits human-readable content while leaving `\href`, `\textbf`, `\begin{rSection}` and all formatting commands completely intact. It assigns confidence scores to every edit and exports an Overleaf-ready ZIP file. Most AI resume tools can't handle raw LaTeX at all.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              SHARED CORE INFRASTRUCTURE          │
│   ChromaDB (vectors) + Ollama (LLM/embeddings)  │
│   + SQLite (persistent memory across sessions)  │
└────────────────┬────────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
┌─────────────┐      ┌──────────────────────┐
│  CAREER     │      │  MISSING PERSONS     │
│  CO-PILOT   │      │  INTELLIGENCE        │
└─────────────┘      └──────────────────────┘
      │                     │
      ▼                     ▼
┌─────────────┐      ┌──────────────────────┐
│ Agent 1     │      │ Agent 1              │
│ Job Scraper │      │ Case Extractor       │
├─────────────┤      ├──────────────────────┤
│ Agent 2     │      │ Agent 2              │
│ Gap Analyzer│      │ Cross-Referencer     │
│ (uses RAG)  │      │ (uses RAG)           │
├─────────────┤      ├──────────────────────┤
│ Agent 3     │      │ Agent 3              │
│ Resume      │      │ Investigator Report  │
│ Rewriter    │      │ Generator            │
├─────────────┤      ├──────────────────────┤
│ Agent 4     │      │ Agent 4              │
│ Interview   │      │ Family Updater       │
│ Prepper     │      │ (compassionate tone) │
└─────────────┘      └──────────────────────┘

Plus:
┌──────────────────────────────────────────┐
│  📄 LaTeX Resume Editor                  │
│  ZIP upload → parse → AI edit → ZIP out  │
│  Confidence scores: 🟢 🟡 🔴             │
│  Never touches URLs, dates, or titles    │
└──────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
hybrid-ai-platform/
│
├── core/                        # Shared infrastructure (used by both sides)
│   ├── embeddings.py            # nomic-embed-text via Ollama
│   ├── vectorstore.py           # ChromaDB wrapper (add, query)
│   └── memory.py                # SQLite — persists weak topics + case logs
│
├── career/                      # Career Co-Pilot
│   ├── agents.py                # 4 career agents
│   ├── prompts.py               # System prompts for each agent
│   ├── pipeline.py              # Orchestrates agents in sequence
│   ├── latex_parser.py          # Parses .tex resume into editable chunks
│   ├── latex_editor.py          # AI editing agent with confidence scores
│   └── job_scraper.py           # URL scraper (Indeed, Glassdoor, generic)
│
├── missing_persons/             # Missing Persons Intelligence
│   ├── agents.py                # 4 case agents
│   ├── prompts.py               # System prompts for each agent
│   └── pipeline.py              # Orchestrates agents in sequence
│
├── ui/
│   ├── app.py                   # Main Gradio app (4 tabs)
│   └── latex_tab.py             # LaTeX Resume Editor tab
│
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed on your machine

```bash
# 1. Pull the models (one-time)
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Clone and set up environment
git clone https://github.com/leemacaravan/hybrid-ai-platform
cd hybrid-ai-platform
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
playwright install chromium     # For JS-heavy job page scraping

# 3. Run
python -m ui.app
```

Open **http://127.0.0.1:7860** in your browser.

---

## 🎯 How to Use

### Career Co-Pilot
1. Paste your experience bullets → **Save to Profile** (stored in RAG)
2. Paste any job description → **Run Career Co-Pilot**
3. Get: job analysis, gap score, rewritten bullets, interview questions

### Missing Persons Intelligence
1. Paste any unstructured report (officer notes, witness tip, intake form)
2. Click **Process Case**
3. Get: structured case data, cross-reference matches, investigator brief, family letter

### LaTeX Resume Editor
1. Zip your `.tex` + `resume.cls` + any assets → upload ZIP
2. Paste a job description (or scrape a URL)
3. Click **Edit My Resume**
4. Review 🟢🟡🔴 confidence-scored changes
5. Download edited ZIP → drag into Overleaf → compile

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| LLM | Ollama (llama3.2) | Local inference, free, private |
| Embeddings | nomic-embed-text | Text → vectors for semantic search |
| Vector DB | ChromaDB | Persistent RAG store |
| Memory | SQLite | Session history, weak topic tracking |
| Agents | CrewAI | Multi-agent orchestration |
| UI | Gradio | Web interface |
| Scraping | BeautifulSoup4 + Playwright | Job URL scraping |
| LaTeX | Custom parser | rSection/itemize/tabular aware |

---

## 🔮 What's Next

- [ ] **PDF Resume Upload** — drag in your PDF, auto-embed into RAG
- [ ] **Suggestion Engine** — project ideas, seniority reframes, metric additions, open source recs, 30-day skill gap plan
- [ ] **Follow-up Chat Agent** — ask follow-up questions after resume edits ("make bullet 3 more aggressive")
- [ ] **Job Application Tracker** — track every application, status, match score history
- [ ] **Public Deployment** — Hugging Face Spaces or VPS with shareable URL

---

## 👩‍💻 About

Built by **Leema Caravan**, CS senior at Rensselaer Polytechnic Institute (RPI), graduating May 2026.

This project was built in a single overnight session as a learning exercise in RAG, multi-agent systems, and local LLM deployment — and as a genuinely useful tool for job searching and supporting real-world missing persons case management.

> *"I wanted to build something that actually helps me, teaches me the most in-demand AI skills, and solves a real problem my dad's app faces — all at once."*

📧 leemacaravan@gmail.com  
🔗 [linkedin.com/in/leema-caravan](https://www.linkedin.com/in/leema-caravan-4738791aa/)  
🌐 [Portfolio](https://leemacaravan.github.io/portfolio-site-/)
