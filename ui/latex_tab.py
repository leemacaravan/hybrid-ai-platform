"""
LaTeX Resume Editor — Gradio UI Tab
"""

import gradio as gr
import os
import sys
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
        if result["success"]:
            status = f"✅ Scraped **{result['site']}** — {result['char_count']} characters extracted"
            return status, result["job_description"]
        else:
            return f"❌ Scrape failed: {result['error']}\n\n*Try pasting the job description manually.*", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""


def process_latex_resume(tex_file, job_description: str):
    """Main handler: parse → edit → diff → return results."""

    if not tex_file:
        return "❌ Please upload your .tex file.", "", "", "", None

    if not job_description.strip():
        return "❌ Please paste a job description.", "", "", "", None

    try:
        with open(tex_file, 'r', encoding='utf-8') as f:
            original_tex = f.read()

        # Step 1: Parse
        chunks = parse_resume(original_tex)
        summary = get_section_summary(chunks)

        parse_status = "✅ **Resume parsed successfully!**\n\n| Section | Chunks Found |\n|---|---|\n"
        parse_status += "\n".join([f"| {k} | {v} |" for k, v in summary.items()])

        # Step 2: Run editor agent
        edit_results = run_latex_editor_agent(chunks, job_description)
        edits = edit_results["edits"]
        tips = edit_results["tips"]

        if not edits:
            return parse_status, "✅ Your resume already matches this job well!", "", "\n".join([f"💡 {t}" for t in tips]), None

        # Step 3: Apply edits
        edited_tex = original_tex
        for edit in edits:
            if edit["original_latex"] in edited_tex:
                edited_tex = edited_tex.replace(edit["original_latex"], edit["new_latex"], 1)

        # Step 4: Build diff display
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

        # Step 5: Tips
        tips_md = "## 💡 Optional Tips\n\n*Things the editor didn't change but recommends:*\n\n"
        for tip in tips:
            tips_md += f"- {tip}\n"
        if not tips:
            tips_md += "_No additional tips!_"

        # Step 6: Save edited .tex
        output_path = "/tmp/resume_edited.tex"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(edited_tex)

        summary_line = f"✅ Made **{len(edits)} changes** ({len(high)} high, {len(medium)} medium, {len(low)} low confidence)"

        return parse_status, summary_line, diff_md, tips_md, output_path

    except Exception as e:
        import traceback
        return f"❌ Error: {str(e)}\n\n{traceback.format_exc()}", "", "", "", None


def build_latex_tab():
    with gr.Tab("📄 LaTeX Resume Editor"):
        gr.Markdown("""
### AI-Powered LaTeX Resume Editor
Upload your `.tex` file + paste a job URL or description → get targeted edits with confidence scores.
**Formatting, dates, company names, and URLs are never touched.**
        """)

        with gr.Row():
            # ── LEFT COLUMN: inputs ──────────────────
            with gr.Column(scale=1):
                tex_upload = gr.File(
                    label="Upload your .tex resume",
                    file_types=[".tex"],
                    type="filepath"
                )

                gr.Markdown("### Job Description")
                gr.Markdown("*Paste a URL and we'll scrape it, or paste the description directly.*")

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

            # ── RIGHT COLUMN: status ─────────────────
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
                gr.Markdown("*Your edited `.tex` file — ready for Overleaf.*")
                download_out = gr.File(label="Download Edited Resume")

        # ── Wire up buttons ──────────────────────────
        scrape_btn.click(
            scrape_url,
            inputs=[url_input],
            outputs=[scrape_status, job_desc_input]
        )

        run_btn.click(
            process_latex_resume,
            inputs=[tex_upload, job_desc_input],
            outputs=[parse_status, summary_out, diff_out, tips_out, download_out]
        )