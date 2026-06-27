from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("applications.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/resumes/", include("resumes.urls")),
    path("api/ai/", include("ai.urls")),
    path("api/interviews/", include("interviews.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/common/", include("common.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
