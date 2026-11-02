from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("accounts.urls")),
    path("gallery/", include("gallery.urls")),
    path("manage/", include("gallery.manage_urls")),
]

if settings.DEBUG:
    # In production serve /media/ from your web server (nginx) or cloud storage.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
