from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("media/", views.MediaManageListView.as_view(), name="media_list"),
    path("media/upload/", views.MediaUploadView.as_view(), name="media_upload"),
    path("media/<int:pk>/edit/", views.MediaUpdateView.as_view(), name="media_edit"),
    path("media/<int:pk>/delete/", views.MediaDeleteView.as_view(), name="media_delete"),
]
