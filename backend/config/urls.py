from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts import api, views
from audit.views import search

urlpatterns = [
    path("api/staff/session/", api.session, name="staff-session-api"),
    path("api/staff/login/", api.sign_in, name="staff-login-api"),
    path("api/staff/logout/", api.sign_out, name="staff-logout-api"),
    path("api/staff/screens/<slug:slug>/", api.screen, name="staff-screen-api"),
    path("api/staff/accounts/", api.accounts, name="staff-accounts-api"),
    path(
        "api/staff/accounts/<int:user_id>/<slug:operation>/",
        api.update_account,
        name="staff-account-update-api",
    ),
    path("api/staff/audit/", search, name="staff-audit-api"),
    path(
        "staff/login/",
        views.StaffLoginView.as_view(template_name="accounts/login.html"),
        name="staff-login",
    ),
    path("staff/logout/", LogoutView.as_view(), name="staff-logout"),
    path("staff/", views.staff_home, name="staff-home"),
    path("staff/foundation/", views.foundation, name="staff-foundation"),
    path("api/foundation/", views.foundation_api, name="foundation-api"),
]
