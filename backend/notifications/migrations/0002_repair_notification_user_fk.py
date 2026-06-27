# Generated to repair a stale PostgreSQL foreign key after switching to the custom user model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE notifications_notification
                DROP CONSTRAINT IF EXISTS notifications_notification_user_id_b5e8c0ff_fk_auth_user_id;

                ALTER TABLE notifications_notification
                DROP CONSTRAINT IF EXISTS notifications_notification_user_id_accounts_userprofile_fk;

                ALTER TABLE notifications_notification
                ADD CONSTRAINT notifications_notification_user_id_accounts_userprofile_fk
                FOREIGN KEY (user_id)
                REFERENCES accounts_userprofile(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE notifications_notification
                DROP CONSTRAINT IF EXISTS notifications_notification_user_id_accounts_userprofile_fk;

                ALTER TABLE notifications_notification
                ADD CONSTRAINT notifications_notification_user_id_b5e8c0ff_fk_auth_user_id
                FOREIGN KEY (user_id)
                REFERENCES auth_user(id)
                DEFERRABLE INITIALLY DEFERRED;
            """,
            state_operations=[
                migrations.AlterField(
                    model_name="notification",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
