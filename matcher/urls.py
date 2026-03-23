from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "matcher"

urlpatterns = [
    path("", views.upload_resume, name="upload_resume"),

    path("history/", views.history, name="history"),
    path("view/<int:resume_id>/", views.view_resume_report, name="resume_view"),
    path("delete/<int:resume_id>/", views.delete_resume, name="delete_resume"),

    path("login/", views.user_login, name="login"),
    path("signup/", views.signup_view, name="signup"),

    path("logout/", auth_views.LogoutView.as_view(next_page="matcher:upload_resume"), name="logout"),
]