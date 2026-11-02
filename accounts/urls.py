from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("manage/login/", views.StaffLoginView.as_view(), name="login"),
    path("manage/logout/", LogoutView.as_view(), name="logout"),  # POST only (Django 5)
    path("manage/password/", views.StaffPasswordChangeView.as_view(), name="password_change"),
]
