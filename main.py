from core.memory import init_db
from core.vectorstore import add_documents
from career.pipeline import run_career_pipeline, print_results
from missing_persons.pipeline import run_missing_persons_pipeline, print_mp_results

init_db()

# ── CAREER SIDE ──────────────────────────────────
my_experience = [
    "Built a REST API using FastAPI and PostgreSQL for a food delivery startup",
    "Developed a React dashboard for real-time inventory tracking",
    "Implemented binary search tree and graph algorithms in C++ for algorithms course",
    "Led a team of 3 to build a mobile app using React Native and Firebase",
    "Wrote unit and integration tests using pytest achieving 90% code coverage",
    "Deployed containerized applications using Docker on AWS EC2",
]
add_documents(
    collection_name="career_experience",
    docs=my_experience,
    ids=[f"exp_{i}" for i in range(len(my_experience))],
    metadata=[{"type": "experience"} for _ in my_experience]
)

sample_job = """
Software Engineer - Backend (Entry Level)
Requirements: Python, FastAPI, PostgreSQL, Docker, unit testing.
Responsibilities: Build backend APIs, write tested code, collaborate with frontend.
"""

print("\n" + "🎯 " * 20)
print("CAREER CO-PILOT")
print("🎯 " * 20)
career_results = run_career_pipeline(sample_job)
print_results(career_results)

# ── MISSING PERSONS SIDE ─────────────────────────
# First case — seed the database
report_1 = """
Reporting party: Campus security officer badge #4421
Date: March 1st, 2026
Missing individual: Maria Gonzalez, 20 years old, Hispanic female.
Last seen leaving the library at 11pm wearing a green jacket and black backpack.
5'3, long dark hair, brown eyes. Has a small scar above her right eyebrow.
Her roommate reported she never returned to the dorm. Parents contacted.
Student ID: MG2024. Emergency contact: Rosa Gonzalez (mother) 305-555-0187.
"""

# Second case — should trigger cross-reference match
report_2 = """
Tip called in March 3rd, 2026 by witness near downtown bus station:
Spotted a young latina woman, approximately 19-21 years old, dark long hair,
around 5'2 or 5'3, looked confused and distressed near the downtown bus terminal.
Was wearing what looked like a green jacket. Did not approach or speak to anyone.
Witness lost sight of her near the east exit around midnight.
"""

print("\n" + "🚨 " * 20)
print("MISSING PERSONS INTELLIGENCE")
print("🚨 " * 20)

print("\n--- Ingesting Case 1 ---")
results_1 = run_missing_persons_pipeline(report_1, case_id="case_MG_001")
print_mp_results(results_1)

print("\n--- Ingesting Case 2 (watch for cross-reference match!) ---")
results_2 = run_missing_persons_pipeline(report_2, case_id="case_tip_001")
print_mp_results(results_2)