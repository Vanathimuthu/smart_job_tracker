# Generated to repair a stale PostgreSQL foreign key after switching to the custom user model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0002_application_apply_link_application_job_description_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE applications_application
                DROP CONSTRAINT IF EXISTS applications_application_user_id_5dae3b8c_fk_auth_user_id;

                ALTER TABLE applications_application
                DROP CONSTRAINT IF EXISTS applications_application_user_id_accounts_userprofile_fk;

                ALTER TABLE applications_application
                ADD CONSTRAINT applications_application_user_id_accounts_userprofile_fk
                FOREIGN KEY (user_id)
                REFERENCES accounts_userprofile(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE applications_application
                DROP CONSTRAINT IF EXISTS applications_application_user_id_accounts_userprofile_fk;

                ALTER TABLE applications_application
                ADD CONSTRAINT applications_application_user_id_5dae3b8c_fk_auth_user_id
                FOREIGN KEY (user_id)
                REFERENCES auth_user(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            state_operations=[
                migrations.AlterField(
                    model_name="application",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
