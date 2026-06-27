KNOWN_SKILLS = [
    "Python",
    "Django",
    "Django REST Framework",
    "REST API",
    "PostgreSQL",
    "Docker",
    "AWS",
    "Redis",
    "Celery",
    "React",
    "Tailwind CSS",
    "Git",
    "SQL",
]

from .ai_client import chat_json


def extract_skills(text):
    lookup = text.lower()
    return [skill for skill in KNOWN_SKILLS if skill.lower() in lookup]


def calculate_match_score(matched_skills_count, total_required_count=0):
    if total_required_count:
        return min(100, round((matched_skills_count / total_required_count) * 100))
    return min(100, max(20, matched_skills_count * 14))


def match_resume_to_job(resume_text, job_description):
    return chat_json(
        "You are a senior recruiter and ATS resume matcher. Return practical, truthful feedback as JSON only.",
        (
            "Compare the resume to the job description. Return only JSON with these keys: "
            "ats_score as an integer 0-100, matched_skills as an array, missing_skills as an array, "
            "resume_improvements as an array of specific changes, role_fit_summary as a short paragraph.\n\n"
            f"Resume:\n{resume_text}\n\nJob description:\n{job_description}"
        ),
    )
