from .ai_client import chat_json


def generate_interview_questions(job_description="", skills=None):
    skills = skills or []
    return chat_json(
        "You are an interview coach. Create role-specific interview preparation questions as JSON only.",
        (
            "Generate interview preparation questions tailored to the job description and skills. "
            "Return only JSON with keys: technical, behavioral, coding, and preparation_tips. "
            "Each key must be an array of concise strings.\n\n"
            f"Skills: {', '.join(skills) if skills else 'Not provided'}\n\n"
            f"Job description:\n{job_description or 'Not provided'}"
        ),
    )
