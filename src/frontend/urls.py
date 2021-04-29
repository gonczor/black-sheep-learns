from django.urls import path
from django.views.generic import TemplateView

app_name = "frontend"

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("gdpr/", TemplateView.as_view(template_name="privacy_policy.html")),
    path("login/", TemplateView.as_view(template_name="login.html")),
    path("courses/", TemplateView.as_view(template_name="courses.html")),
    path("courses/<int:id>/", TemplateView.as_view(template_name="course_details.html")),
]
