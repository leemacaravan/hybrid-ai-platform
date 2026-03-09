"""
LaTeX Resume Parser — tailored for rSection/itemize/tabular structure.
Extracts editable sections without touching LaTeX formatting commands.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LatexChunk:
    """A single editable chunk extracted from the resume."""
    section: str
    chunk_type: str
    original: str
    content: str
    start_idx: int
    end_idx: int


def strip_latex(text: str) -> str:
    """Remove common LaTeX commands to get readable content."""
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)
    for cmd in [r'\\textbf', r'\\textit', r'\\emph', r'\\vspace\{[^}]+\}',
                r'\\hfill', r'\\newline', r'\\\\', r'\\item', r'\\itemsep[^{}]*']:
        text = re.sub(cmd + r'\{([^}]*)\}', r'\1', text)
        text = re.sub(cmd, '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'\{|\}', '', text)
    return ' '.join(text.split()).strip()


def parse_resume(tex_content: str) -> list[LatexChunk]:
    """
    Parse a .tex resume into editable chunks.
    Returns list of LatexChunk objects for each editable piece.
    """
    chunks = []

    # ── 1. OBJECTIVE ─────────────────────────────
    obj_match = re.search(
        r'(\\begin\{rSection\}\{OBJECTIVE\})(.*?)(\\end\{rSection\})',
        tex_content, re.DOTALL | re.IGNORECASE
    )
    if obj_match:
        inner = obj_match.group(2)
        text_lines = [l.strip() for l in inner.split('\n')
                      if l.strip() and not l.strip().startswith('\\vspace')
                      and not l.strip().startswith('%')]
        if text_lines:
            original = '\n'.join(text_lines)
            chunks.append(LatexChunk(
                section="OBJECTIVE",
                chunk_type="objective",
                original=original,
                content=strip_latex(original),
                start_idx=obj_match.start(2),
                end_idx=obj_match.end(2)
            ))

    # ── 2. SKILLS (tabular rows) ──────────────────
    skills_match = re.search(
        r'(\\begin\{rSection\}\{SKILLS\})(.*?)(\\end\{rSection\})',
        tex_content, re.DOTALL | re.IGNORECASE
    )
    if skills_match:
        inner = skills_match.group(2)
        row_pattern = re.compile(r'([A-Za-z/\s]+:)\s*&\s*([^\\\n]+?)(?:\\\\|$)', re.MULTILINE)
        for row in row_pattern.finditer(inner):
            full_row = row.group(0).strip()
            category = row.group(1).strip()
            values = row.group(2).strip()
            chunks.append(LatexChunk(
                section="SKILLS",
                chunk_type="skills_row",
                original=full_row,
                content=f"{category} {values}",
                start_idx=skills_match.start(2) + row.start(),
                end_idx=skills_match.start(2) + row.end()
            ))

    # ── 3. EXPERIENCE (bullet items) ─────────────
    exp_match = re.search(
        r'(\\begin\{rSection\}\{EXPERIENCE\})(.*?)(\\end\{rSection\})',
        tex_content, re.DOTALL | re.IGNORECASE
    )
    if exp_match:
        inner = exp_match.group(2)
        offset = exp_match.start(2)

        title_pattern = re.compile(
            r'(\\textbf\{[^}]+\}[^\n]*(?:\\href[^\n]*)?[^\n]*\\hfill[^\n]*\n)',
            re.MULTILINE
        )
        for m in title_pattern.finditer(inner):
            chunks.append(LatexChunk(
                section="EXPERIENCE",
                chunk_type="summary_line",
                original=m.group(0).strip(),
                content=strip_latex(m.group(0)),
                start_idx=offset + m.start(),
                end_idx=offset + m.end()
            ))

        bullet_pattern = re.compile(
            r'\\item\s+(?!\[)(.+?)(?=\\item|\\end\{itemize\}|\\vspace)',
            re.DOTALL
        )
        for m in bullet_pattern.finditer(inner):
            bullet_text = m.group(0).strip()
            readable = strip_latex(bullet_text)
            if len(readable) > 20:
                chunks.append(LatexChunk(
                    section="EXPERIENCE",
                    chunk_type="bullet",
                    original=bullet_text,
                    content=readable,
                    start_idx=offset + m.start(),
                    end_idx=offset + m.end()
                ))

    # ── 4. PROJECTS ───────────────────────────────
    proj_match = re.search(
        r'(\\begin\{rSection\}\{PROJECTS\})(.*?)(\\end\{rSection\})',
        tex_content, re.DOTALL | re.IGNORECASE
    )
    if proj_match:
        inner = proj_match.group(2)
        offset = proj_match.start(2)

        proj_item_pattern = re.compile(
            r'\\item\s+\\textbf\{([^}]+)\}(.*?)(?=\\item|\\end\{rSection\}|$)',
            re.DOTALL
        )
        for m in proj_item_pattern.finditer(inner):
            full = m.group(0).strip()
            readable = strip_latex(full)
            if len(readable) > 20:
                chunks.append(LatexChunk(
                    section="PROJECTS",
                    chunk_type="bullet",
                    original=full,
                    content=readable,
                    start_idx=offset + m.start(),
                    end_idx=offset + m.end()
                ))

    return chunks


def get_section_summary(chunks: list[LatexChunk]) -> dict:
    """Summarize what was parsed for display."""
    summary = {}
    for chunk in chunks:
        summary[chunk.section] = summary.get(chunk.section, 0) + 1
    return summary


def apply_edits(tex_content: str, edits: list[dict]) -> str:
    """
    Apply a list of edits to the tex content.
    Each edit: {"original": str, "replacement": str}
    """
    result = tex_content
    for edit in edits:
        original = edit["original"]
        replacement = edit["replacement"]
        if original in result:
            result = result.replace(original, replacement, 1)
    return result