"""
LaTeX Resume Editor Agent
Takes parsed chunks + job description → returns targeted edits with confidence scores.
"""

import ollama
import json
import re
from career.latex_parser import LatexChunk


EDITOR_SYSTEM_PROMPT = """You are an expert resume editor specializing in LaTeX resumes.

Your job is to improve resume content to better match a job description.

STRICT RULES:
1. Return ONLY valid JSON — no markdown, no explanation
2. Keep ALL LaTeX commands intact (\\textbf, \\item, \\href, etc.)
3. Only change the human-readable text content inside commands
4. Never change dates, company names, job titles, or URLs
5. Keep edits natural — don't keyword-stuff
6. Assign a confidence score 0-100 for each edit

Return this exact JSON structure:
{
  "edits": [
    {
      "original_content": "exact readable content as given",
      "improved_content": "your improved version",
      "confidence": 85,
      "reason": "Added relevant keywords to match job requirements",
      "change_type": "keyword_alignment"
    }
  ],
  "tips": [
    "Optional tip about something you recommend considering"
  ]
}

If a chunk doesn't need changes, don't include it in edits.
change_type must be one of: keyword_alignment, impact_metric, clarity, skills_addition
"""


def call_llm(system_prompt: str, user_message: str) -> dict:
    """Call local Ollama and parse JSON response."""
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    raw = response["message"]["content"]
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    start = clean.find("{")
    end = clean.rfind("}") + 1
    return json.loads(clean[start:end])


def reconstruct_latex(original_latex: str, original_content: str, new_content: str) -> str:
    """
    Splice new content back into LaTeX, preserving all commands.
    """
    # Skills rows: "Category: & values \\"
    if '&' in original_latex:
        parts = original_latex.split('&', 1)
        category_part = parts[0]
        values_part = parts[1] if len(parts) > 1 else ''
        trailing = ''
        if '\\\\' in values_part:
            trailing = '\\\\'
        new_values = new_content
        if ':' in new_content:
            new_values = new_content.split(':', 1)[1].strip()
        return f"{category_part}& {new_values} {trailing}"

    # Objective: simple text
    if '\\begin' not in original_latex and '\\item' not in original_latex:
        return new_content

    # Bullets: preserve \item prefix and any hrefs
    item_prefix_match = re.match(
        r'(\\item\s*(?:\\itemsep[^{}]*\s*)?(?:\{[^}]*\}\s*)?(?:\\vspace\{[^}]*\}\s*)?)',
        original_latex
    )
    if item_prefix_match:
        prefix = item_prefix_match.group(1)
        hrefs = re.findall(r'\\href\{[^}]+\}\{[^}]+\}', original_latex)
        result = prefix + new_content
        for href in hrefs:
            href_display = re.search(r'\\href\{[^}]+\}\{([^}]+)\}', href)
            if href_display and href_display.group(1) not in new_content:
                result += f" {href}"
        return result

    return original_latex


def run_latex_editor_agent(chunks: list[LatexChunk], job_description: str) -> dict:
    """
    Main editor agent: takes parsed chunks + job description,
    returns edits with confidence scores and tips.
    """
    print("\n🤖 LaTeX Editor Agent is analyzing your resume...")

    chunks_text = ""
    for i, chunk in enumerate(chunks):
        chunks_text += f"\n[{i}] Section: {chunk.section} | Type: {chunk.chunk_type}\n"
        chunks_text += f"Content: {chunk.content}\n"

    user_message = f"""Job Description:
{job_description}

Resume chunks to potentially improve:
{chunks_text}

Return JSON with edits and tips as specified."""

    result = call_llm(EDITOR_SYSTEM_PROMPT, user_message)

    # Match edits back to original chunks and reconstruct LaTeX
    final_edits = []
    for edit in result.get("edits", []):
        matched_chunk = None
        for chunk in chunks:
            if edit.get("original_content", "").strip().lower() in chunk.content.lower():
                matched_chunk = chunk
                break
            # Fuzzy match
            orig_words = set(edit.get("original_content", "").lower().split())
            chunk_words = set(chunk.content.lower().split())
            if len(orig_words) > 3 and len(orig_words & chunk_words) / len(orig_words) > 0.6:
                matched_chunk = chunk
                break

        if matched_chunk:
            new_latex = reconstruct_latex(
                matched_chunk.original,
                matched_chunk.content,
                edit["improved_content"]
            )
            final_edits.append({
                "section": matched_chunk.section,
                "chunk_type": matched_chunk.chunk_type,
                "original_latex": matched_chunk.original,
                "new_latex": new_latex,
                "original_content": matched_chunk.content,
                "improved_content": edit["improved_content"],
                "confidence": edit.get("confidence", 70),
                "reason": edit.get("reason", ""),
                "change_type": edit.get("change_type", "keyword_alignment")
            })

    return {
        "edits": final_edits,
        "tips": result.get("tips", [])
    }


def generate_diff(original_tex: str, edited_tex: str) -> list[dict]:
    """Generate a human-readable diff between original and edited resume."""
    original_lines = original_tex.split('\n')
    edited_lines = edited_tex.split('\n')

    diff = []
    for i, (orig, edit) in enumerate(zip(original_lines, edited_lines)):
        if orig != edit:
            diff.append({
                "line": i + 1,
                "type": "changed",
                "original": orig,
                "edited": edit,
            })
    return diff