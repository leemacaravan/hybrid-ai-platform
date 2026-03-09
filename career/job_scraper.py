"""
Job URL Scraper
Handles LinkedIn, Indeed, Glassdoor, and generic company career pages.
Uses requests+BS4 for simple pages, Playwright for JS-heavy ones.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# ── Site detection ────────────────────────────────────────────────────────────

def detect_site(url: str) -> str:
    """Detect which job site the URL is from."""
    domain = urlparse(url).netloc.lower()
    if "linkedin.com" in domain:
        return "linkedin"
    if "indeed.com" in domain:
        return "indeed"
    if "glassdoor.com" in domain:
        return "glassdoor"
    return "generic"


# ── Simple scraper (requests + BS4) ──────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_simple(url: str) -> str:
    """Scrape a simple static page."""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "advertisement", "iframe"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def scrape_with_playwright(url: str) -> str:
    """Scrape a JS-rendered page using Playwright (for LinkedIn etc)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="en-US"
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for job content to load
            page.wait_for_timeout(2000)
            content = page.content()
            browser.close()

        soup = BeautifulSoup(content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    except Exception as e:
        raise Exception(f"Playwright scrape failed: {e}")


# ── Site-specific extractors ──────────────────────────────────────────────────

def extract_linkedin(raw_text: str) -> str:
    """Extract job description from LinkedIn raw text."""
    lines = raw_text.split("\n")
    result = []
    capture = False

    keywords_start = ["about the job", "job description", "responsibilities",
                      "qualifications", "requirements", "what you'll do",
                      "what we're looking for", "about this role"]
    keywords_stop = ["show more", "show less", "apply now", "save job",
                     "report this job", "similar jobs", "people also viewed"]

    for line in lines:
        line_lower = line.lower().strip()

        if any(kw in line_lower for kw in keywords_start):
            capture = True

        if capture:
            if any(kw in line_lower for kw in keywords_stop):
                break
            if line.strip():
                result.append(line.strip())

    return "\n".join(result) if result else raw_text[:3000]


def extract_indeed(raw_text: str) -> str:
    """Extract job description from Indeed raw text."""
    lines = raw_text.split("\n")
    result = []
    capture = False

    for line in lines:
        line_lower = line.lower().strip()
        if "job description" in line_lower or "full job description" in line_lower:
            capture = True
            continue
        if capture:
            if "report job" in line_lower or "indeed" in line_lower[:20]:
                break
            if line.strip():
                result.append(line.strip())

    return "\n".join(result) if result else raw_text[:3000]


def extract_glassdoor(raw_text: str) -> str:
    """Extract job description from Glassdoor raw text."""
    lines = raw_text.split("\n")
    result = []
    capture = False

    for line in lines:
        line_lower = line.lower().strip()
        if "job description" in line_lower or "overview" in line_lower:
            capture = True
            continue
        if capture:
            if "company overview" in line_lower or "see all jobs" in line_lower:
                break
            if line.strip():
                result.append(line.strip())

    return "\n".join(result) if result else raw_text[:3000]


def extract_generic(raw_text: str, url: str) -> str:
    """
    Generic extractor for company career pages.
    Finds the densest block of job-related text.
    """
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    # Score each line for job-relevance
    job_keywords = [
        "responsibilities", "requirements", "qualifications", "experience",
        "skills", "bachelor", "master", "degree", "years", "proficient",
        "strong", "knowledge", "ability", "team", "collaborate", "develop",
        "build", "design", "implement", "manage", "lead", "python", "java",
        "javascript", "react", "aws", "sql", "api", "agile", "scrum"
    ]

    scored_lines = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        score = sum(1 for kw in job_keywords if kw in line_lower)
        scored_lines.append((score, i, line))

    # Find the region with highest density of job keywords
    if not scored_lines:
        return raw_text[:3000]

    best_score = max(s[0] for s in scored_lines)
    if best_score == 0:
        return raw_text[:3000]

    # Find center of high-scoring region
    high_scoring = [s for s in scored_lines if s[0] >= max(1, best_score // 2)]
    if not high_scoring:
        return raw_text[:3000]

    center_idx = high_scoring[len(high_scoring) // 2][1]
    start = max(0, center_idx - 30)
    end = min(len(lines), center_idx + 60)

    return "\n".join(lines[start:end])


def clean_extracted_text(text: str) -> str:
    """Final cleanup of extracted job description."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove very short lines (likely UI noise)
    lines = [l for l in text.split('\n') if len(l.strip()) > 2]
    # Limit to reasonable length
    result = '\n'.join(lines)
    return result[:4000].strip()


# ── Main entry point ─────────────────────────────────────────────────────────

def scrape_job_url(url: str) -> dict:
    """
    Main function: takes any job URL → returns extracted job description.
    Returns: {"success": bool, "job_description": str, "site": str, "error": str}
    """
    site = detect_site(url)
    print(f"🔍 Detected site: {site}")

    try:
        # Try simple scrape first (faster)
        try:
            raw_text = scrape_simple(url)
            print(f"   Simple scrape: {len(raw_text)} chars")
        except Exception:
            # Fall back to Playwright for JS-heavy sites
            print(f"   Simple scrape failed, trying Playwright...")
            raw_text = scrape_with_playwright(url)
            print(f"   Playwright scrape: {len(raw_text)} chars")

        # Site-specific extraction
        if site == "linkedin":
            extracted = extract_linkedin(raw_text)
        elif site == "indeed":
            extracted = extract_indeed(raw_text)
        elif site == "glassdoor":
            extracted = extract_glassdoor(raw_text)
        else:
            extracted = extract_generic(raw_text, url)

        cleaned = clean_extracted_text(extracted)

        if len(cleaned) < 100:
            # Too short — probably got blocked, try Playwright
            print("   Content too short, retrying with Playwright...")
            raw_text = scrape_with_playwright(url)
            extracted = extract_generic(raw_text, url)
            cleaned = clean_extracted_text(extracted)

        return {
            "success": True,
            "job_description": cleaned,
            "site": site,
            "char_count": len(cleaned),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "job_description": "",
            "site": site,
            "char_count": 0,
            "error": str(e)
        }