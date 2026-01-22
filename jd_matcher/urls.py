from django.urls import path
from .views import jd_matcher_view

urlpatterns = [
    path("jd-match/", jd_matcher_view, name="jd_match"),
]
