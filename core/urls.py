from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    # staff inbox
    path("manage/messages/", views.MessageListView.as_view(), name="messages_manage"),
    path("manage/messages/<int:pk>/toggle/", views.MessageToggleReadView.as_view(), name="message_toggle"),
    path("manage/messages/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
]
