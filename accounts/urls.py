from django.urls import path
from accounts.views import signup, login_view

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
]

