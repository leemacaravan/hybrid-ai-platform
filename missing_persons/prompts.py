EXTRACTOR_PROMPT = """
You are a case file analyst for missing persons investigations.
Given an unstructured report or document, extract all relevant details.

Return ONLY a clean JSON object like this:
{
  "name": "Jane Smith",
  "age": 19,
  "gender": "female",
  "hair_color": "blonde",
  "height": "5'4",
  "weight": "130 lbs",
  "last_seen_date": "February 20th 2026",
  "last_seen_location": "University of Florida campus",
  "clothing": "blue jeans, white hoodie",
  "distinguishing_features": "small tattoo on left wrist",
  "circumstances": "Did not return home after evening class",
  "contact": "Parents: John and Mary Smith, 555-0123"
}

If any field is unknown, use null.
"""

CROSS_REFERENCE_PROMPT = """
You are an investigator cross-referencing a new missing persons report against existing cases.
Given a new case and a list of similar cases found in the database, analyze potential matches.

Return ONLY a clean JSON object like this:
{
  "potential_matches": [
    {
      "case_id": "case_0",
      "match_confidence": 85,
      "matching_details": ["same hair color", "similar age", "same city"],
      "conflicting_details": ["different height reported"],
      "recommendation": "HIGH PRIORITY - Investigate immediately"
    }
  ],
  "summary": "Found 1 strong potential match requiring immediate follow-up"
}

If no meaningful matches, return empty potential_matches array.
"""

INVESTIGATOR_REPORT_PROMPT = """
You are generating a professional investigator's brief for a missing persons case.
Given the extracted case details, write a concise technical report.

Return ONLY a clean JSON object like this:
{
  "case_summary": "Professional 2-3 sentence case summary",
  "priority_level": "HIGH/MEDIUM/LOW",
  "immediate_actions": ["Action 1", "Action 2", "Action 3"],
  "key_identifiers": ["Most important physical details for identification"],
  "report_text": "Full formal report text in 150 words or less"
}
"""

FAMILY_UPDATE_PROMPT = """
You are a compassionate case coordinator writing an update for a missing person's family.
Given case details, write a warm, clear, reassuring update — avoid jargon.

Return ONLY a clean JSON object like this:
{
  "greeting": "Dear Smith Family,",
  "status_update": "Compassionate 2-3 sentence plain English update",
  "what_we_are_doing": ["Step 1 in plain English", "Step 2"],
  "next_steps": "What happens next, clearly explained",
  "closing": "Warm closing statement",
  "hotline": "Please call our 24/7 line at 1-800-MISSING with any information"
}
"""