from django.apps import AppConfig


class InterviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "interviews"
    
    def ready(self):
        # Register signal handlers
        import interviews.signals  # noqa: F401
