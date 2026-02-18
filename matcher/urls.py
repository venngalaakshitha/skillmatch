from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 🔥 MAIN APP ROUTES
    path("", views.upload_resume, name="upload_resume"),
    path('upload/', views.upload_resume, name='upload'),
    path("history/", views.history, name="history"),
    path("download-report/<int:resume_id>/", views.download_resume_report, name="download_resume_report"),
    path("resume/<int:resume_id>/delete/", views.delete_resume, name="delete_resume"),
    
    # 🔥 AUTHENTICATION ROUTES
    path("login/", views.user_login, name="login"),
    path("signup/", views.signup_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page='upload_resume'), name="logout"),
]
