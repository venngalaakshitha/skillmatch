from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "matcher"

urlpatterns = [
    # Landing page
    path('', views.index, name='index'),

    # Upload page
    path('upload/', views.upload_resume, name='upload_resume'),

    # Other pages
    path("history/", views.history, name="history"),
    path("view/<int:resume_id>/", views.view_resume_report, name="resume_view"),
    path("delete/<int:resume_id>/", views.delete_resume, name="delete_resume"),

    # Auth
    path("login/", views.user_login, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(next_page="matcher:index"), name="logout"),
]