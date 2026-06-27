# Generated to repair a stale PostgreSQL foreign key after switching to the custom user model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_job_apply_link_job_date_saved_job_role_job_salary_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE jobs_job
                DROP CONSTRAINT IF EXISTS jobs_job_user_id_093659ab_fk_auth_user_id;

                ALTER TABLE jobs_job
                DROP CONSTRAINT IF EXISTS jobs_job_user_id_accounts_userprofile_fk;

                ALTER TABLE jobs_job
                ADD CONSTRAINT jobs_job_user_id_accounts_userprofile_fk
                FOREIGN KEY (user_id)
                REFERENCES accounts_userprofile(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE jobs_job
                DROP CONSTRAINT IF EXISTS jobs_job_user_id_accounts_userprofile_fk;

                ALTER TABLE jobs_job
                ADD CONSTRAINT jobs_job_user_id_093659ab_fk_auth_user_id
                FOREIGN KEY (user_id)
                REFERENCES auth_user(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            state_operations=[
                migrations.AlterField(
                    model_name="job",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
