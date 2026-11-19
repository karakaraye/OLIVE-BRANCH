from hashlib import sha256
from uuid import UUID, uuid4

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from django.utils import timezone

from accounts.models import StaffProfile
from audit.models import AuditEvent

SESSION_VERSION = "staff_session_version"
SESSION_STARTED = "staff_session_started"


def session_version(user):
    return (
        StaffProfile.objects.filter(user=user)
        .values_list("session_version", flat=True)
        .first()
        or 0
    )


def client_request_id(request):
    value = request.headers.get("Idempotency-Key") or request.POST.get("request_id")
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        return None


def authentication_event(request, action, user, username, reason):
    key = client_request_id(request) if request is not None else None
    record = f"staff:{user.pk}" if user else f"login:{username.casefold()}"
    identity = f"{action}:{record}:{key or uuid4()}"
    AuditEvent.objects.get_or_create(
        request_id=sha256(identity.encode()).hexdigest(),
        defaults={
            "action": action,
            "actor": user,
            "actor_label": username,
            "reason": reason,
            "affected_record": record,
        },
    )


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    request.session[SESSION_VERSION] = session_version(user)
    if SESSION_STARTED not in request.session:
        request.session[SESSION_STARTED] = int(timezone.now().timestamp())
    authentication_event(
        request,
        AuditEvent.Action.LOGIN,
        user,
        user.get_username(),
        "Staff signed in",
    )


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    if user and user.is_authenticated:
        authentication_event(
            request,
            AuditEvent.Action.LOGOUT,
            user,
            user.get_username(),
            getattr(request, "staff_logout_reason", "Staff signed out"),
        )


@receiver(user_login_failed)
def audit_failed_login(sender, credentials, request, **kwargs):
    username = str(credentials.get("username", ""))[:150]
    authentication_event(
        request,
        AuditEvent.Action.LOGIN_FAILED,
        None,
        username,
        "Staff credentials were rejected",
    )


class StaffSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            version = request.session.get(SESSION_VERSION)
            started = request.session.get(SESSION_STARTED, 0)
            if version != session_version(request.user):
                request.staff_logout_reason = "Staff session was revoked"
                logout(request)
            elif timezone.now().timestamp() >= started + settings.SESSION_COOKIE_AGE:
                request.staff_logout_reason = "Staff session expired"
                logout(request)
        return self.get_response(request)
