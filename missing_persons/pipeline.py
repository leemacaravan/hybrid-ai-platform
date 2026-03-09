from missing_persons.agents import (
    agent_extractor,
    agent_cross_referencer,
    agent_report_generator,
    agent_family_updater
)
import uuid

def run_missing_persons_pipeline(raw_report: str, case_id: str = None) -> dict:
    """Full Missing Persons pipeline. Pass in any unstructured report."""
    if not case_id:
        case_id = f"case_{uuid.uuid4().hex[:8]}"
    
    print(f"🚨 Starting Missing Persons pipeline for case: {case_id}\n")
    print("=" * 50)
    
    # Agent 1 → extract structured data + store in vector DB
    case_data = agent_extractor(raw_report, case_id)
    
    # Agent 2 → cross-reference against all existing cases
    cross_ref = agent_cross_referencer(case_data)
    
    # Agent 3 → investigator report
    report = agent_report_generator(case_data, cross_ref)
    
    # Agent 4 → family update
    family_update = agent_family_updater(case_data, report)
    
    print("\n" + "=" * 50)
    print("✅ Missing persons pipeline complete!\n")
    
    return {
        "case_id": case_id,
        "extracted_data": case_data,
        "cross_reference": cross_ref,
        "investigator_report": report,
        "family_update": family_update
    }

def print_mp_results(results: dict):
    """Pretty print missing persons pipeline output."""
    
    print(f"\n🆔 CASE ID: {results['case_id']}")
    
    d = results["extracted_data"]
    print(f"\n👤 EXTRACTED CASE DATA")
    print(f"  Name: {d.get('name')} | Age: {d.get('age')} | Gender: {d.get('gender')}")
    print(f"  Last seen: {d.get('last_seen_date')} at {d.get('last_seen_location')}")
    print(f"  Description: {d.get('hair_color')} hair, {d.get('height')}")
    print(f"  Circumstances: {d.get('circumstances')}")
    
    cr = results["cross_reference"]
    print(f"\n🔍 CROSS-REFERENCE RESULTS")
    print(f"  {cr.get('summary', 'No summary')}")
    for match in cr.get("potential_matches", []):
        print(f"  ⚠️  Match confidence: {match.get('match_confidence')}%")
        print(f"     Matching: {match.get('matching_details')}")
        print(f"     ➡️  {match.get('recommendation')}")
    
    r = results["investigator_report"]
    print(f"\n📋 INVESTIGATOR BRIEF")
    print(f"  Priority: {r.get('priority_level')}")
    print(f"  Summary: {r.get('case_summary')}")
    print(f"  Immediate actions:")
    for action in r.get("immediate_actions", []):
        print(f"    → {action}")
    
    f = results["family_update"]
    print(f"\n💙 FAMILY COMMUNICATION")
    print(f"  {f.get('greeting')}")
    print(f"  {f.get('status_update')}")
    print(f"  {f.get('closing')}")
    print(f"  {f.get('hotline')}")