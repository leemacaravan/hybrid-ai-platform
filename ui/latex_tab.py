"""
LaTeX Resume Editor — Gradio UI Tab
Accepts ZIP (containing .tex + .cls + assets), exports edited ZIP.
"""

import gradio as gr
import os
import sys
import tempfile
import zipfile
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from career.latex_parser import parse_resume, get_section_summary
from career.latex_editor import run_latex_editor_agent, generate_diff


def scrape_url(url: str):
    """Scrape a job URL and return the description."""
    if not url.strip():
        return "❌ Please enter a URL.", ""
    try:
        from career.job_scraper import scrape_job_url
        result = scrape_job_url(url.strip())

        if result.get("error") == "linkedin_blocked":
            return """⚠️ **LinkedIn blocks automated scraping** (they require login).

**Easy workaround — 30 seconds:**
1. Open the LinkedIn job posting in your browser
2. Scroll to the **"About the job"** section
3. Select all that text → Copy
4. Paste it into the Job Description box below""", ""

        if result["success"]:
            status = f"✅ Scraped **{result['site']}** — {result['char_count']} characters extracted"
            return status, result["job_description"]
        else:
            return f"❌ Scrape failed: {result['error']}\n\n*Try pasting the job description manually.*", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""


def extract_zip(zip_path: str) -> tuple[str, str, list[str]]:
    """
    Extract ZIP to a temp dir.
    Returns: (extract_dir, tex_file_path, all_file_paths)
    """
    extract_dir = os.path.join(tempfile.gettempdir(), "resume_zip_extract")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    tex_file = None
    all_files = []
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            full_path = os.path.join(root, f)
            all_files.append(full_path)
            if f.endswith('.tex') and tex_file is None:
                tex_file = full_path

    return extract_dir, tex_file, all_files


def build_output_zip(extract_dir: str, edited_tex: str, original_tex_path: str) -> str:
    """
    Build a new ZIP with the edited .tex + all original support files.
    Returns path to the new ZIP.
    """
    with open(original_tex_path, 'w', encoding='utf-8') as f:
        f.write(edited_tex)

    output_zip_path = os.path.join(tempfile.gettempdir(), "resume_edited.zip")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_dir)
                zf.write(file_path, arcname)

    return output_zip_path


def process_latex_resume(zip_file, job_description: str):
    """Main handler: unzip → parse → edit → rezip → return results."""

    if not zip_file:
        return "❌ Please upload your resume ZIP file.", "", "", "", None

    if not job_description.strip():
        return "❌ Please paste a job description.", "", "", "", None

    try:
        # Step 1: Extract ZIP
        extract_dir, tex_path, all_files = extract_zip(zip_file)

        if not tex_path:
            return "❌ No .tex file found in ZIP.", "", "", "", None

        file_list = "\n".join([f"  • {os.path.basename(f)}" for f in all_files])

        with open(tex_path, 'r', encoding='utf-8') as f:
            original_tex = f.read()

        # Step 2: Parse
        chunks = parse_resume(original_tex)
        summary = get_section_summary(chunks)

        parse_status = f"✅ **ZIP extracted — {len(all_files)} files found:**\n{file_list}\n\n"
        parse_status += "**Resume sections parsed:**\n\n| Section | Chunks |\n|---|---|\n"
        parse_status += "\n".join([f"| {k} | {v} |" for k, v in summary.items()])

        # Step 3: Run editor agent
        edit_results = run_latex_editor_agent(chunks, job_description)
        edits = edit_results["edits"]
        tips = edit_results["tips"]

        if not edits:
            return parse_status, "✅ Your resume already matches this job well!", "", "\n".join([f"💡 {t}" for t in tips]), None

        # Step 4: Apply edits
        edited_tex = original_tex
        for edit in edits:
            if edit["original_latex"] in edited_tex:
                edited_tex = edited_tex.replace(edit["original_latex"], edit["new_latex"], 1)

        # Step 5: Build diff display
        diff_md = "## 📝 Changes Made\n\n"

        high   = [e for e in edits if e["confidence"] >= 80]
        medium = [e for e in edits if 60 <= e["confidence"] < 80]
        low    = [e for e in edits if e["confidence"] < 60]

        def render_group(edit_list, emoji, label):
            if not edit_list:
                return ""
            out = f"### {emoji} {label}\n\n"
            for e in edit_list:
                orig = e['original_content'][:120] + ('...' if len(e['original_content']) > 120 else '')
                new  = e['improved_content'][:120] + ('...' if len(e['improved_content']) > 120 else '')
                out += f"**[{e['section']}]** _{e['change_type'].replace('_', ' ').title()}_\n\n"
                out += f"~~{orig}~~\n\n"
                out += f"**→ {new}**\n\n"
                out += f"*Confidence: {e['confidence']}% — {e['reason']}*\n\n---\n\n"
            return out

        diff_md += render_group(high,   "🟢", "High Confidence (80%+) — Safe to keep")
        diff_md += render_group(medium, "🟡", "Medium Confidence (60-79%) — Review before using")
        diff_md += render_group(low,    "🔴", "Low Confidence (<60%) — Your call")

        # Step 6: Tips
        tips_md = "## 💡 Optional Tips\n\n*Things the editor didn't change but recommends:*\n\n"
        for tip in tips:
            tips_md += f"- {tip}\n"
        if not tips:
            tips_md += "_No additional tips!_"

        # Step 7: Build output ZIP
        output_zip = build_output_zip(extract_dir, edited_tex, tex_path)

        summary_line = (
            f"✅ Made **{len(edits)} changes** "
            f"({len(high)} high, {len(medium)} medium, {len(low)} low confidence)\n\n"
            f"📦 Download the ZIP below and upload directly to Overleaf!"
        )

        return parse_status, summary_line, diff_md, tips_md, output_zip

    except Exception as e:
        import traceback
        return f"❌ Error: {str(e)}\n\n{traceback.format_exc()}", "", "", "", None


def build_latex_tab():
    with gr.Tab("📄 LaTeX Resume Editor"):
        gr.Markdown("""
### AI-Powered LaTeX Resume Editor
Upload your resume **ZIP file** (containing `.tex` + `resume.cls` + any assets) → get targeted edits → download an Overleaf-ready ZIP.
**Formatting, dates, company names, and URLs are never touched.**
        """)

        with gr.Row():
            with gr.Column(scale=1):

                gr.Markdown("### 1. Upload Resume ZIP")
                gr.Markdown("*Zip your `.tex`, `resume.cls`, and `qr_code.png` together, then upload.*")
                zip_upload = gr.File(
                    label="Upload resume ZIP",
                    file_types=[".zip"],
                    type="filepath"
                )

                gr.Markdown("### 2. Job Description")
                gr.Markdown("*Paste a URL to scrape, or paste the description directly.*")

                with gr.Row():
                    url_input = gr.Textbox(
                        label="Job URL (optional)",
                        placeholder="https://linkedin.com/jobs/view/... or any job posting URL",
                        scale=3
                    )
                    scrape_btn = gr.Button("🔗 Scrape", variant="secondary", scale=1)

                scrape_status = gr.Markdown("")

                job_desc_input = gr.Textbox(
                    label="Job Description",
                    placeholder="Paste the full job posting here, or scrape a URL above...",
                    lines=10
                )

                run_btn = gr.Button("🚀 Edit My Resume", variant="primary", size="lg")

            with gr.Column(scale=2):
                parse_status = gr.Markdown("")
                summary_out  = gr.Markdown("")

        gr.Markdown("---")

        with gr.Tabs():
            with gr.Tab("📝 Changes"):
                diff_out = gr.Markdown("")
            with gr.Tab("💡 Tips"):
                tips_out = gr.Markdown("")
            with gr.Tab("⬇️ Download"):
                gr.Markdown("*Download your edited ZIP — drag it straight into Overleaf to compile.*")
                download_out = gr.File(label="Download Edited Resume ZIP")

        scrape_btn.click(
            scrape_url,
            inputs=[url_input],
            outputs=[scrape_status, job_desc_input]
        )

        run_btn.click(
            process_latex_resume,
            inputs=[zip_upload, job_desc_input],
            outputs=[parse_status, summary_out, diff_out, tips_out, download_out]
        )