from .ai_client import chat_text


def rewrite_resume_section(section_text, target_role=""):
    return chat_text(
        "You are an expert resume writer. Rewrite resume bullets in a concise, ATS-friendly, achievement-focused style.",
        (
            "Rewrite this resume section. Keep it truthful, professional, and specific. "
            "Do not invent employer names, numbers, or technologies not present in the input. "
            "Return only the rewritten resume text.\n\n"
            f"Target role: {target_role or 'Not specified'}\n\n"
            f"Resume section:\n{section_text}"
        ),
    )
