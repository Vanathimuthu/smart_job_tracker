# Generated to repair a stale PostgreSQL foreign key after switching to the custom user model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0002_resume_ats_score_resume_is_default_resume_skills_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE resumes_resume
                DROP CONSTRAINT IF EXISTS resumes_resume_user_id_0221d0a3_fk_auth_user_id;

                ALTER TABLE resumes_resume
                DROP CONSTRAINT IF EXISTS resumes_resume_user_id_accounts_userprofile_fk;

                ALTER TABLE resumes_resume
                ADD CONSTRAINT resumes_resume_user_id_accounts_userprofile_fk
                FOREIGN KEY (user_id)
                REFERENCES accounts_userprofile(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE resumes_resume
                DROP CONSTRAINT IF EXISTS resumes_resume_user_id_accounts_userprofile_fk;

                ALTER TABLE resumes_resume
                ADD CONSTRAINT resumes_resume_user_id_0221d0a3_fk_auth_user_id
                FOREIGN KEY (user_id)
                REFERENCES auth_user(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            state_operations=[
                migrations.AlterField(
                    model_name="resume",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resumes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
