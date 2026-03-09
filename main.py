from core.memory import init_db
from core.vectorstore import add_documents, query

# 1. Initialize memory
init_db()

# 2. Test the career side — store some fake resume experience
career_docs = [
    "Built a REST API using FastAPI and PostgreSQL for a food delivery startup",
    "Developed a React dashboard for real-time inventory tracking",
    "Implemented a binary search tree in C++ for an algorithms course",
    "Led a team of 3 to build a mobile app using React Native and Firebase",
]
add_documents(
    collection_name="career_experience",
    docs=career_docs,
    ids=[f"exp_{i}" for i in range(len(career_docs))],
    metadata=[{"type": "experience"} for _ in career_docs]
)

# 3. Test retrieval — simulate a job posting asking for backend skills
print("\n🔍 Searching for backend-relevant experience...")
results = query("career_experience", "backend API development Python", n_results=2)
for r in results:
    print(f"  → {r['text']}")

# 4. Test the missing persons side — store a fake case
case_docs = [
    "John Doe, age 34, last seen March 1st near downtown Miami. Brown hair, 6ft tall, wearing a red jacket.",
    "Jane Smith, age 19, missing since February 20th. Last seen at University of Florida campus. Blonde hair, 5'4.",
]
add_documents(
    collection_name="missing_cases",
    docs=case_docs,
    ids=[f"case_{i}" for i in range(len(case_docs))],
    metadata=[{"status": "open"} for _ in case_docs]
)

# 5. Test case cross-reference
print("\n🔍 Cross-referencing new sighting report...")
results = query("missing_cases", "young woman seen near university blonde hair", n_results=1)
for r in results:
    print(f"  → {r['text']}")

print("\n✅ Day 1 complete — shared core is working!")