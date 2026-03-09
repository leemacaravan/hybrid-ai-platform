from career.agents import (
    agent_job_scraper,
    agent_gap_analyzer,
    agent_resume_rewriter,
    agent_interview_prepper
)

def run_career_pipeline(job_description: str) -> dict:
    """
    Full Career Co-Pilot pipeline.
    Runs all 4 agents in sequence, passing outputs forward.
    """
    print("🚀 Starting Career Co-Pilot pipeline...\n")
    print("=" * 50)
    
    # Agent 1 → scrape job
    job_data = agent_job_scraper(job_description)
    
    # Agent 2 → gap analysis (uses RAG internally)
    gap_data = agent_gap_analyzer(job_data)
    
    # Agent 3 → rewrite resume (uses output from agents 1 + 2)
    resume_data = agent_resume_rewriter(job_data, gap_data)
    
    # Agent 4 → interview prep (uses job data + memory)
    interview_data = agent_interview_prepper(job_data)
    
    print("\n" + "=" * 50)
    print("✅ Pipeline complete!\n")
    
    return {
        "job_analysis": job_data,
        "gap_analysis": gap_data,
        "rewritten_resume": resume_data,
        "interview_prep": interview_data
    }

def print_results(results: dict):
    """Pretty print the full pipeline output."""
    
    print("\n📋 JOB ANALYSIS")
    print(f"  Required skills: {results['job_analysis'].get('required_skills', [])}")
    print(f"  Experience needed: {results['job_analysis'].get('experience_years', '?')} years")
    
    print("\n📊 GAP ANALYSIS")
    print(f"  Match score: {results['gap_analysis'].get('match_score', '?')}/100")
    print(f"  ✅ You have: {results['gap_analysis'].get('matching_skills', [])}")
    print(f"  ❌ You're missing: {results['gap_analysis'].get('missing_skills', [])}")
    print(f"  💡 Advice: {results['gap_analysis'].get('advice', '')}")
    
    print("\n✍️  REWRITTEN RESUME BULLETS")
    for bullet in results['rewritten_resume'].get('rewritten_bullets', []):
        print(f"  • {bullet}")
    
    print("\n🎯 INTERVIEW PREP")
    print("  Technical Questions:")
    for q in results['interview_prep'].get('technical_questions', []):
        print(f"  Q: {q.get('question', '')}")
        print(f"  💡 Tip: {q.get('tip', '')}\n")