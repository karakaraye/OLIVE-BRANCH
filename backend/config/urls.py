from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accounts import views

urlpatterns = [
    path(
        "staff/login/",
        LoginView.as_view(template_name="accounts/login.html"),
        name="staff-login",
    ),
    path("staff/logout/", LogoutView.as_view(), name="staff-logout"),
    path("staff/", views.staff_home, name="staff-home"),
    path("staff/foundation/", views.foundation, name="staff-foundation"),
    path("api/foundation/", views.foundation_api, name="foundation-api"),
]
