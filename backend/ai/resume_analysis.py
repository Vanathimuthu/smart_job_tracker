import re

from .ai_client import chat_json
from .prompts import RESUME_ANALYSIS_SYSTEM_PROMPT


def build_fallback_resume_analysis(resume_text, job_description):
    resume_tokens = re.findall(r"[a-zA-Z]+", resume_text)
    job_tokens = re.findall(r"[a-zA-Z]+", job_description)

    resume_lookup = {token.lower(): token for token in resume_tokens}
    overlap = []
    seen = set()

    for token in job_tokens:
        key = token.lower()
        if len(key) > 3 and key in resume_lookup and key not in seen:
            overlap.append(resume_lookup[key])
            seen.add(key)

    overlap = sorted(overlap, key=lambda word: word.lower())
    recommendations = overlap[:5]
    ats_score = min(100, max(20, len(overlap) * 14))
    ignored_words = {"the", "and", "with", "for", "experience", "role", "engineer"}
    skill_gap_analysis = [
        skill
        for skill in sorted(set(job_tokens), key=lambda word: word.lower())
        if len(skill) > 3
        and skill.lower() not in resume_lookup
        and skill.lower() not in ignored_words
    ][:5]
    interview_questions = [
        f"Tell me about your experience with {skill}." for skill in skill_gap_analysis[:3]
    ]

    if not recommendations:
        recommendations = [
            "Add job-specific keywords",
            "Highlight measurable achievements",
            "Tailor your summary to the role",
        ]

    return {
        "match_score": ats_score,
        "ats_score": ats_score,
        "matched_skills": overlap[:8],
        "recommendations": recommendations,
        "skill_gap_analysis": skill_gap_analysis,
        "ai_interview_questions": interview_questions,
        "ai_summary": (
            "Your resume shows solid overlap with the role, but the strongest opportunities are to strengthen "
            "the job-specific evidence and tailor your language to the employer's requirements."
        ),
    }


def analyze_resume(resume_text, job_description):
    return chat_json(
        RESUME_ANALYSIS_SYSTEM_PROMPT,
        (
            "Analyze this resume against the job description. Return only JSON with these keys: "
            "ats_score as an integer 0-100, matched_skills as an array, recommendations as an array, "
            "skill_gap_analysis as an array, ai_interview_questions as an array, ai_summary as a short paragraph.\n\n"
            f"Resume:\n{resume_text}\n\nJob description:\n{job_description}"
        )
    )
