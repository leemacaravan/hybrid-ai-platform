import ollama
import json
from career.prompts import (
    JOB_SCRAPER_PROMPT,
    GAP_ANALYZER_PROMPT,
    RESUME_REWRITER_PROMPT,
    INTERVIEW_PREP_PROMPT
)
from core.vectorstore import query
from core.memory import get_weak_topics

def call_llm(system_prompt: str, user_message: str) -> dict:
    """Call local Ollama LLM and parse JSON response."""
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    raw = response["message"]["content"]
    # Strip markdown fences
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    # Extract just the JSON object if there's extra text around it
    start = clean.find("{")
    end = clean.rfind("}") + 1
    json_str = clean[start:end]
    return json.loads(json_str)

def agent_job_scraper(job_description: str) -> dict:
    """Agent 1: Extract structured data from a job posting."""
    print("\n🤖 Agent 1 (Job Scraper) is analyzing the job posting...")
    result = call_llm(JOB_SCRAPER_PROMPT, f"Job posting:\n{job_description}")
    print(f"   Found {len(result.get('required_skills', []))} required skills")
    return result

def agent_gap_analyzer(job_data: dict) -> dict:
    """Agent 2: Compare candidate experience vs job requirements using RAG."""
    print("\n🤖 Agent 2 (Gap Analyzer) is comparing your experience...")
    
    # RAG: pull the most relevant experience for this job
    skill_query = " ".join(job_data.get("required_skills", []))
    relevant_experience = query("career_experience", skill_query, n_results=4)
    experience_text = "\n".join([r["text"] for r in relevant_experience])
    
    user_message = f"""
Candidate experience (most relevant to this job):
{experience_text}

Job required skills: {job_data.get('required_skills', [])}
Job responsibilities: {job_data.get('responsibilities', [])}
"""
    result = call_llm(GAP_ANALYZER_PROMPT, user_message)
    print(f"   Match score: {result.get('match_score', '?')}/100")
    return {**result, "experience_used": experience_text}

def agent_resume_rewriter(job_data: dict, gap_data: dict) -> dict:
    """Agent 3: Rewrite resume bullets to match the job."""
    print("\n🤖 Agent 3 (Resume Rewriter) is rewriting your bullets...")
    
    user_message = f"""
Original experience bullets:
{gap_data.get('experience_used', '')}

Target job required skills: {job_data.get('required_skills', [])}
Target job responsibilities: {job_data.get('responsibilities', [])}
Matching skills to emphasize: {gap_data.get('matching_skills', [])}
"""
    result = call_llm(RESUME_REWRITER_PROMPT, user_message)
    print(f"   Generated {len(result.get('rewritten_bullets', []))} rewritten bullets")
    return result

def agent_interview_prepper(job_data: dict) -> dict:
    """Agent 4: Generate interview questions based on job + weak topics."""
    print("\n🤖 Agent 4 (Interview Prepper) is generating questions...")
    
    weak_topics = get_weak_topics(limit=3)
    
    user_message = f"""
Job required skills: {job_data.get('required_skills', [])}
Job responsibilities: {job_data.get('responsibilities', [])}
Candidate weak topics to focus on: {weak_topics if weak_topics else ['general CS fundamentals']}
"""
    result = call_llm(INTERVIEW_PREP_PROMPT, user_message)
    print(f"   Generated {len(result.get('technical_questions', []))} technical questions")
    return result