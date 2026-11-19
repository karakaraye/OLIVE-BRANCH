from django.conf import settings
from django.db import models

from .roles import ROLE_SCREENS, screen_permission


class StaffAccess(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("access_staff", "Can access the staff workspace"),
            ("view_foundation", "Can review foundation records"),
            ("search_audit", "Can search audit events"),
            *(
                (screen_permission(screen), f"Can access {title}")
                for screen, title, _ in ROLE_SCREENS.values()
            ),
        ]


class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_version = models.PositiveIntegerField(default=0)
    outlet = models.ForeignKey(
        "outlets.Outlet", on_delete=models.PROTECT, blank=True, null=True
    )
