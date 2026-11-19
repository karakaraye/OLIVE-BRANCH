from django.db import models


class StaffAccess(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("access_staff", "Can access the staff workspace"),
            ("view_foundation", "Can review foundation records"),
        ]
