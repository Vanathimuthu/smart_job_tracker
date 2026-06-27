import re

from django.db import migrations


ROLE_KEYWORDS = {
    "backend": {"python", "django", "rest", "api", "sql", "postgresql", "mysql", "authentication", "database"},
    "frontend": {"react", "javascript", "typescript", "html", "css", "tailwind", "responsive", "ui"},
    "full stack": {"python", "django", "react", "javascript", "api", "sql", "html", "css"},
    "python": {"python", "django", "rest", "api", "sql", "postgresql", "mysql"},
    "django": {"python", "django", "rest", "api", "orm", "postgresql"},
}


def tokenize(text):
    return {token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text or "")}


def calculate_score(resume):
    evidence_text = " ".join([resume.content or "", resume.skills or ""])
    if not tokenize(evidence_text):
        return 0

    text = " ".join([resume.content or "", resume.skills or "", resume.target_role or "", resume.title or ""])
    tokens = tokenize(text)
    if not tokens:
        return 0

    role_text = f"{resume.target_role} {resume.title}".lower()
    expected = set()
    for role, keywords in ROLE_KEYWORDS.items():
        if role in role_text:
            expected.update(keywords)

    if not expected:
        expected = {"python", "django", "react", "javascript", "sql", "api", "database", "html", "css"}

    keyword_score = round((len(expected & tokens) / len(expected)) * 70)
    detail_score = min(20, len(tokens) // 8)
    evidence_score = 10 if any(char.isdigit() for char in text) else 0
    return min(100, keyword_score + detail_score + evidence_score)


def recalculate_resume_scores(apps, schema_editor):
    Resume = apps.get_model("resumes", "Resume")
    for resume in Resume.objects.all():
        score = calculate_score(resume)
        if resume.ats_score != score:
            resume.ats_score = score
            resume.save(update_fields=["ats_score"])


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0004_backfill_resume_ats_scores"),
    ]

    operations = [
        migrations.RunPython(recalculate_resume_scores, migrations.RunPython.noop),
    ]
