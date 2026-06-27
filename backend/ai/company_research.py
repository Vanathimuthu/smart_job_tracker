from .ai_client import chat_json


def research_company(company, job_description=""):
    return chat_json(
        "You are a company research assistant for job candidates. Be useful, cautious, and do not invent recent news.",
        (
            "Create interview-focused company research. If current facts are uncertain, say what to verify. "
            "Return only JSON with keys: company_overview, products, tech_stack, recent_news, interview_tips, questions_to_ask. "
            "Use arrays for products, tech_stack, recent_news, interview_tips, and questions_to_ask.\n\n"
            f"Company: {company}\n\nJob description:\n{job_description or 'Not provided'}"
        ),
    )
