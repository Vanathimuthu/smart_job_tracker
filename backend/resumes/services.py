import re


ROLE_KEYWORDS = {
    "backend": {"python", "django", "rest", "api", "sql", "postgresql", "mysql", "authentication", "database"},
    "frontend": {"react", "javascript", "typescript", "html", "css", "tailwind", "responsive", "ui"},
    "full stack": {"python", "django", "react", "javascript", "api", "sql", "html", "css"},
    "python": {"python", "django", "rest", "api", "sql", "postgresql", "mysql"},
    "django": {"python", "django", "rest", "api", "orm", "postgresql"},
}


def tokenize(text):
    return {token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text or "")}


def calculate_resume_ats_score(content="", skills="", target_role="", title=""):
    evidence_text = " ".join([content or "", skills or ""])
    if not tokenize(evidence_text):
        return 0

    text = " ".join([content or "", skills or "", target_role or "", title or ""])
    tokens = tokenize(text)
    if not tokens:
        return 0

    role_text = f"{target_role} {title}".lower()
    expected = set()
    for role, keywords in ROLE_KEYWORDS.items():
        if role in role_text:
            expected.update(keywords)

    if not expected:
        expected = {"python", "django", "react", "javascript", "sql", "api", "database", "html", "css"}

    matched = expected & tokens
    keyword_score = round((len(matched) / len(expected)) * 70)
    detail_score = min(20, len(tokens) // 8)
    evidence_score = 10 if any(char.isdigit() for char in text) else 0

    return min(100, keyword_score + detail_score + evidence_score)
