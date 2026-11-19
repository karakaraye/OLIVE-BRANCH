from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    class Action(models.TextChoices):
        SEED = "seed", "Demo seed"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        LOGIN_FAILED = "login_failed", "Failed login"
        ACCOUNT_CREATED = "account_created", "Account created"
        ROLE_CHANGED = "role_changed", "Role changed"
        ACCOUNT_DISABLED = "account_disabled", "Account disabled"
        ACCOUNT_ENABLED = "account_enabled", "Account enabled"

    request_id = models.CharField(max_length=100, unique=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True
    )
    actor_label = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=24, choices=Action, default=Action.SEED)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reason = models.CharField(max_length=255)
    affected_record = models.CharField(max_length=255, db_index=True)
    details = models.JSONField(default=dict, blank=True)
