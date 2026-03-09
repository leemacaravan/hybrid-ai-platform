import gradio as gr
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.latex_tab import build_latex_tab
from core.memory import init_db
from core.vectorstore import add_documents
from career.pipeline import run_career_pipeline
from missing_persons.pipeline import run_missing_persons_pipeline

# Initialize on startup
init_db()

# ── CAREER FUNCTIONS ─────────────────────────────

def load_experience(experience_text: str) -> str:
    """Load user's experience into the vector store."""
    lines = [l.strip() for l in experience_text.strip().split("\n") if l.strip()]
    if not lines:
        return "❌ Please enter at least one experience bullet."
    add_documents(
        collection_name="career_experience",
        docs=lines,
        ids=[f"exp_{i}" for i in range(len(lines))],
        metadata=[{"type": "experience"} for _ in lines]
    )
    return f"✅ Loaded {len(lines)} experience bullets into your profile!"

def run_career(job_description: str):
    """Run full career pipeline and return formatted results."""
    if not job_description.strip():
        return "❌ Please paste a job description.", "", "", ""
    
    try:
        results = run_career_pipeline(job_description)
        
        # Job Analysis
        job = results["job_analysis"]
        job_out = f"""**Required Skills:** {', '.join(job.get('required_skills', []))}
**Experience Needed:** {job.get('experience_years', '?')} years
**Nice to Have:** {', '.join(job.get('nice_to_have', []))}"""

        # Gap Analysis
        gap = results["gap_analysis"]
        gap_out = f"""**Match Score: {gap.get('match_score', '?')}/100**

✅ **You Have:** {', '.join(gap.get('matching_skills', []))}
❌ **You're Missing:** {', '.join(gap.get('missing_skills', []))}

💡 **Advice:** {gap.get('advice', '')}"""

        # Rewritten Bullets
        bullets = results["rewritten_resume"].get("rewritten_bullets", [])
        bullets_out = "\n\n".join([f"• {b}" for b in bullets])

        # Interview Prep
        interview = results["interview_prep"]
        interview_out = "**Technical Questions:**\n\n"
        for q in interview.get("technical_questions", []):
            interview_out += f"**Q:** {q.get('question', '')}\n"
            interview_out += f"💡 *{q.get('tip', '')}*\n\n"
        interview_out += "\n**Behavioral Questions:**\n\n"
        for q in interview.get("behavioral_questions", []):
            interview_out += f"**Q:** {q.get('question', '')}\n"
            interview_out += f"💡 *{q.get('tip', '')}*\n\n"

        return job_out, gap_out, bullets_out, interview_out

    except Exception as e:
        return f"❌ Error: {str(e)}", "", "", ""

# ── MISSING PERSONS FUNCTIONS ─────────────────────

def run_missing_persons(report: str, case_id: str):
    """Run full missing persons pipeline and return formatted results."""
    if not report.strip():
        return "❌ Please enter a case report.", "", "", ""
    
    case_id = case_id.strip() or None
    
    try:
        results = run_missing_persons_pipeline(report, case_id=case_id)
        
        # Extracted Data
        d = results["extracted_data"]
        extracted_out = f"""**Name:** {d.get('name') or 'Unknown (anonymous tip)'}
**Age:** {d.get('age') or 'Unknown'} | **Gender:** {d.get('gender') or 'Unknown'}
**Last Seen:** {d.get('last_seen_date')} at {d.get('last_seen_location')}
**Description:** {d.get('hair_color')} hair, {d.get('height')}
**Clothing:** {d.get('clothing') or 'Unknown'}
**Distinguishing Features:** {d.get('distinguishing_features') or 'None noted'}
**Circumstances:** {d.get('circumstances')}
**Contact:** {d.get('contact') or 'None provided'}
**Case ID:** {results['case_id']}"""

        # Cross Reference
        cr = results["cross_reference"]
        cross_out = f"**{cr.get('summary', 'No summary')}**\n\n"
        for match in cr.get("potential_matches", []):
            confidence = match.get('match_confidence', 0)
            emoji = "🔴" if confidence >= 80 else "🟡" if confidence >= 60 else "🟢"
            cross_out += f"{emoji} **Match Confidence: {confidence}%**\n"
            cross_out += f"✅ Matching: {', '.join(match.get('matching_details', []))}\n"
            if match.get('conflicting_details'):
                cross_out += f"⚠️ Conflicting: {', '.join(match.get('conflicting_details', []))}\n"
            cross_out += f"➡️ **{match.get('recommendation')}**\n\n"

        # Investigator Report
        r = results["investigator_report"]
        priority_emoji = "🔴" if r.get('priority_level') == 'HIGH' else "🟡" if r.get('priority_level') == 'MEDIUM' else "🟢"
        report_out = f"""{priority_emoji} **Priority: {r.get('priority_level')}**

**Summary:** {r.get('case_summary')}

**Immediate Actions:**
{chr(10).join([f"→ {a}" for a in r.get('immediate_actions', [])])}

---
{r.get('report_text', '')}"""

        # Family Update
        f = results["family_update"]
        family_out = f"""{f.get('greeting')}

{f.get('status_update')}

**What we are doing:**
{chr(10).join([f"• {s}" for s in f.get('what_we_are_doing', [])])}

**Next Steps:** {f.get('next_steps')}

{f.get('closing')}

_{f.get('hotline')}_"""

        return extracted_out, cross_out, report_out, family_out

    except Exception as e:
        return f"❌ Error: {str(e)}", "", "", ""

# ── GRADIO UI ─────────────────────────────────────

with gr.Blocks(title="Hybrid AI Platform") as app:
    gr.HTML("""
    <div class="header">
        <h1>🤖 Hybrid AI Platform</h1>
        <p style="color: #666; font-size: 1.1em;">
            Career Co-Pilot &nbsp;|&nbsp; Missing Persons Intelligence
        </p>
        <p style="color: #999; font-size: 0.9em;">
            Powered by Ollama (local LLM) + ChromaDB (RAG) + CrewAI
        </p>
    </div>
    """)

    with gr.Tabs():

        # ── CAREER TAB ──────────────────────────────
        with gr.Tab("🎯 Career Co-Pilot"):
            gr.Markdown("### Step 1: Load Your Experience")
            gr.Markdown("*Paste your experience bullets — one per line. This gets stored in your personal RAG database.*")
            
            with gr.Row():
                with gr.Column(scale=2):
                    experience_input = gr.Textbox(
                        label="Your Experience (one bullet per line)",
                        placeholder="""Built a REST API using FastAPI and PostgreSQL for a food delivery startup
Developed a React dashboard for real-time inventory tracking
Led a team of 3 to build a mobile app using React Native and Firebase
Deployed containerized applications using Docker on AWS EC2""",
                        lines=6
                    )
                with gr.Column(scale=1):
                    load_btn = gr.Button("💾 Save to Profile", variant="secondary", size="lg")
                    load_status = gr.Markdown("")
            
            load_btn.click(load_experience, inputs=[experience_input], outputs=[load_status])

            gr.Markdown("---")
            gr.Markdown("### Step 2: Paste a Job Description")
            
            job_input = gr.Textbox(
                label="Job Description",
                placeholder="Paste any job posting here...",
                lines=8
            )
            career_btn = gr.Button("🚀 Run Career Co-Pilot", variant="primary", size="lg")

            gr.Markdown("### Results")
            with gr.Row():
                with gr.Column():
                    job_out = gr.Markdown(label="📋 Job Analysis")
                with gr.Column():
                    gap_out = gr.Markdown(label="📊 Gap Analysis")
            
            gr.Markdown("### ✍️ Rewritten Resume Bullets")
            bullets_out = gr.Markdown()
            
            gr.Markdown("### 🎯 Interview Prep")
            interview_out = gr.Markdown()

            career_btn.click(
                run_career,
                inputs=[job_input],
                outputs=[job_out, gap_out, bullets_out, interview_out]
            )

        # ── MISSING PERSONS TAB ─────────────────────
        with gr.Tab("🚨 Missing Persons Intelligence"):
            gr.Markdown("### Submit Case Report or Tip")
            gr.Markdown("*Paste any unstructured report — official intake form, witness tip, officer notes, anything.*")

            with gr.Row():
                with gr.Column(scale=3):
                    report_input = gr.Textbox(
                        label="Case Report / Witness Tip",
                        placeholder="""Example: Missing individual: Maria Gonzalez, 20 years old...
OR
Tip: Witness spotted a young woman near downtown bus station...""",
                        lines=8
                    )
                with gr.Column(scale=1):
                    case_id_input = gr.Textbox(
                        label="Case ID (optional)",
                        placeholder="e.g. case_001 or leave blank"
                    )
                    mp_btn = gr.Button("🚨 Process Case", variant="primary", size="lg")

            gr.Markdown("### Results")
            with gr.Row():
                with gr.Column():
                    extracted_out = gr.Markdown(label="👤 Extracted Case Data")
                with gr.Column():
                    cross_out = gr.Markdown(label="🔍 Cross-Reference Results")
            
            with gr.Row():
                with gr.Column():
                    report_out = gr.Markdown(label="📋 Investigator Brief")
                with gr.Column():
                    family_out = gr.Markdown(label="💙 Family Communication")

            mp_btn.click(
                run_missing_persons,
                inputs=[report_input, case_id_input],
                outputs=[extracted_out, cross_out, report_out, family_out]
            )
		# ── LATEX RESUME EDITOR TAB ─────────────────
        build_latex_tab()

        # ── ABOUT TAB ───────────────────────────────
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
## 🏗️ Architecture

This platform runs **100% locally** — no data leaves your machine.

### Shared Core
- **Ollama** (llama3.2) — Local LLM, free, private
- **nomic-embed-text** — Local embeddings
- **ChromaDB** — Vector database for RAG
- **SQLite** — Persistent memory across sessions

### Career Co-Pilot Agents
1. **Job Scraper** — Extracts skills/requirements from any job posting
2. **Gap Analyzer** — RAG-powered comparison of your experience vs. job
3. **Resume Rewriter** — Rewrites your bullets with job-specific keywords
4. **Interview Prepper** — Generates questions adapted to your weak spots

### Missing Persons Intelligence Agents  
1. **Extractor** — Parses unstructured reports into structured data
2. **Cross-Referencer** — Semantic search across all cases for matches
3. **Report Generator** — Professional investigator brief
4. **Family Updater** — Compassionate plain-English family communication

### Stack
`Python` · `Ollama` · `ChromaDB` · `CrewAI` · `Gradio` · `FastAPI` · `SQLite`
            """)

if __name__ == "__main__":
	import tempfile
	app.launch(share=False, server_port=7860, allowed_paths=[tempfile.gettempdir()])