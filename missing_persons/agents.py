import ollama
import json
from missing_persons.prompts import (
    EXTRACTOR_PROMPT,
    CROSS_REFERENCE_PROMPT,
    INVESTIGATOR_REPORT_PROMPT,
    FAMILY_UPDATE_PROMPT
)
from core.vectorstore import query, add_documents
from core.memory import log_case_event

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

def agent_extractor(raw_report: str, case_id: str) -> dict:
    """Agent 1: Extract structured data from unstructured report."""
    print("\n🤖 Agent 1 (Extractor) is parsing the case report...")
    result = call_llm(EXTRACTOR_PROMPT, f"Case report:\n{raw_report}")
    
    # Store in vector DB for future cross-referencing
    doc_text = f"""
    Name: {result.get('name')} | Age: {result.get('age')} | Gender: {result.get('gender')}
    Hair: {result.get('hair_color')} | Height: {result.get('height')}
    Last seen: {result.get('last_seen_date')} at {result.get('last_seen_location')}
    Circumstances: {result.get('circumstances')}
    Features: {result.get('distinguishing_features')}
    """
    add_documents(
        collection_name="missing_cases",
        docs=[doc_text.strip()],
        ids=[case_id],
        metadata=[{
    "case_id": case_id, 
    "name": result.get("name") or "Unknown", 
    "status": "open"
}]
    )
    log_case_event(case_id, f"Case ingested: {result.get('name', 'Unknown')}")
    print(f"   Extracted case for: {result.get('name', 'Unknown')}")
    return {**result, "case_id": case_id}

def agent_cross_referencer(case_data: dict) -> dict:
    """Agent 2: Search all existing cases for potential matches."""
    print("\n🤖 Agent 2 (Cross-Referencer) is searching all cases...")
    
    # RAG: search by physical description + location
    search_query = f"""
    {case_data.get('gender', '')} {case_data.get('hair_color', '')} hair
    age {case_data.get('age', '')} last seen {case_data.get('last_seen_location', '')}
    {case_data.get('distinguishing_features', '')}
    """
    similar_cases = query("missing_cases", search_query, n_results=3)
    
    # Filter out the case itself
    other_cases = [
        c for c in similar_cases
        if case_data.get("case_id") not in c.get("metadata", {}).get("case_id", "")
    ]
    
    if not other_cases:
        print("   No similar cases found in database")
        return {"potential_matches": [], "summary": "No matches found in current database"}
    
    cases_text = "\n\n".join([f"Case {i+1}: {c['text']}" for i, c in enumerate(other_cases)])
    user_message = f"""
New case:
Name: {case_data.get('name')} | Age: {case_data.get('age')}
Hair: {case_data.get('hair_color')} | Last seen: {case_data.get('last_seen_location')}
Features: {case_data.get('distinguishing_features')}

Existing cases to compare against:
{cases_text}
"""
    result = call_llm(CROSS_REFERENCE_PROMPT, user_message)
    matches = len(result.get("potential_matches", []))
    print(f"   Found {matches} potential match(es)")
    if matches > 0:
        log_case_event(case_data["case_id"], f"Cross-reference found {matches} potential match(es)")
    return result

def agent_report_generator(case_data: dict, cross_ref_data: dict) -> dict:
    """Agent 3: Generate professional investigator report."""
    print("\n🤖 Agent 3 (Report Generator) is writing the investigator brief...")
    
    user_message = f"""
Case details:
{json.dumps(case_data, indent=2)}

Cross-reference results:
{json.dumps(cross_ref_data, indent=2)}
"""
    result = call_llm(INVESTIGATOR_REPORT_PROMPT, user_message)
    print(f"   Priority level: {result.get('priority_level', '?')}")
    log_case_event(case_data["case_id"], f"Report generated - Priority: {result.get('priority_level')}")
    return result

def agent_family_updater(case_data: dict, report_data: dict) -> dict:
    """Agent 4: Generate compassionate family-facing update."""
    print("\n🤖 Agent 4 (Family Updater) is writing the family communication...")
    
    user_message = f"""
Case details:
Name: {case_data.get('name')} | Last seen: {case_data.get('last_seen_date')}
Location: {case_data.get('last_seen_location')}
Circumstances: {case_data.get('circumstances')}
Priority: {report_data.get('priority_level')}
Immediate actions being taken: {report_data.get('immediate_actions', [])}
"""
    result = call_llm(FAMILY_UPDATE_PROMPT, user_message)
    print(f"   Family update written for: {case_data.get('name', 'Unknown')}")
    return result