from .ai_client import chat_text


def answer_career_question(question, resume_text="", job_description=""):
    return chat_text(
        "You are a practical career coach. Give concise, specific advice grounded in the user's resume and target job.",
        (
            "Answer the career question. Use the resume and job description when provided. "
            "Keep the response actionable and avoid generic filler.\n\n"
            f"Question:\n{question}\n\nResume:\n{resume_text or 'Not provided'}\n\n"
            f"Job description:\n{job_description or 'Not provided'}"
        ),
    )
