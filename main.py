from core.memory import init_db
from core.vectorstore import add_documents, query
from career.pipeline import run_career_pipeline, print_results

# Initialize
init_db()

# Load YOUR experience into the vector store
# (Replace these with your real experience!)
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

# Paste any real job description here
sample_job = """
Software Engineer - Backend (Entry Level)
We are looking for a backend engineer to join our team.
Requirements:
- 1-2 years experience with Python
- Experience with REST APIs and FastAPI or Django
- Familiarity with SQL databases (PostgreSQL preferred)
- Basic understanding of Docker and containerization
- Experience writing unit tests
- Bonus: AWS experience, React knowledge
Responsibilities:
- Build and maintain backend APIs
- Write clean, tested, documented code
- Collaborate with frontend team
- Participate in code reviews
"""

# Run the full pipeline
results = run_career_pipeline(sample_job)
print_results(results)